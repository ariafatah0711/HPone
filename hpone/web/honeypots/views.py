from __future__ import annotations

from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import HoneypotYamlForm
from services import hpone_service
from hpone_web.auth import verify
from hpone_web.middleware import set_auth_cookie

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        if verify(username, password):
            next_url = request.GET.get("next") or "/"
            response = redirect(next_url)
            set_auth_cookie(response, username)
            return response
        return render(
            request,
            "honeypots/login.html",
            {"error": "Invalid credentials"},
        )
    return render(request, "honeypots/login.html")

def dashboard(request):
    honeypots = hpone_service.list_honeypots()
    context = {
        "honeypots": honeypots,
        "breadcrumbs": [
            {"label": "Dashboard", "url": "/", "active": True}
        ],
    }
    return render(request, "honeypots/dashboard.html", context)

@require_GET
def detail(request, honeypot_id: str):
    try:
        detail_data = hpone_service.get_honeypot_detail(honeypot_id)
    except hpone_service.HoneypotNotFound:
        raise Http404("Honeypot not found")
    detail_data["breadcrumbs"] = [
        {"label": "Dashboard", "url": "/", "active": False},
        {"label": detail_data.get("name", honeypot_id), "url": None, "active": True},
    ]
    return render(request, "honeypots/detail.html", detail_data)

@require_POST
def start_honeypot(request, honeypot_id: str):
    try:
        hpone_service.start_honeypot(honeypot_id, force=False)
        messages.success(request, f"Started {honeypot_id}.")
    except Exception as exc:
        messages.error(request, f"Failed to start {honeypot_id}: {exc}")
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("honeypot-detail", honeypot_id=honeypot_id)


@require_POST
def stop_honeypot(request, honeypot_id: str):
    try:
        hpone_service.stop_honeypot(honeypot_id)
        messages.success(request, f"Stopped {honeypot_id}.")
    except Exception as exc:
        messages.error(request, f"Failed to stop {honeypot_id}: {exc}")
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("honeypot-detail", honeypot_id=honeypot_id)


@require_POST
def enable_honeypot(request, honeypot_id: str):
    try:
        hpone_service.enable_honeypot(honeypot_id, True)
        messages.success(request, f"Enabled {honeypot_id}.")
    except Exception as exc:
        messages.error(request, f"Failed to enable {honeypot_id}: {exc}")
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("honeypot-detail", honeypot_id=honeypot_id)


@require_POST
def disable_honeypot(request, honeypot_id: str):
    try:
        hpone_service.enable_honeypot(honeypot_id, False)
        messages.success(request, f"Disabled {honeypot_id}.")
    except Exception as exc:
        messages.error(request, f"Failed to disable {honeypot_id}: {exc}")
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("honeypot-detail", honeypot_id=honeypot_id)

@require_GET
def logs(request, honeypot_id: str):
    lines = int(request.GET.get("lines", "200"))
    try:
        output = hpone_service.get_logs(honeypot_id, lines=lines)
    except Exception as exc:
        output = f"Failed to fetch logs: {exc}"
    return HttpResponse(output, content_type="text/plain")


def edit_yaml(request, honeypot_id: str):
    breadcrumb_name = honeypot_id
    if request.method == "POST":
        form = HoneypotYamlForm(request.POST)
        if form.is_valid():
            try:
                hpone_service.write_yaml_text(honeypot_id, form.cleaned_data["content"])
                messages.success(request, "Saved YAML configuration.")
                return redirect("honeypot-detail", honeypot_id=honeypot_id)
            except Exception as exc:
                messages.error(request, f"Failed to save YAML: {exc}")
    else:
        try:
            content = hpone_service.read_yaml_text(honeypot_id)
            try:
                detail_data = hpone_service.get_honeypot_detail(honeypot_id)
                breadcrumb_name = detail_data.get("name", honeypot_id)
            except Exception:
                breadcrumb_name = honeypot_id
        except Exception:
            raise Http404("Honeypot not found")
        form = HoneypotYamlForm(initial={"content": content})

    return render(
        request,
        "honeypots/edit_yaml.html",
        {
            "form": form,
            "honeypot_id": honeypot_id,
            "breadcrumbs": [
                {"label": "Dashboard", "url": "/", "active": False},
                {"label": breadcrumb_name, "url": f"/honeypots/{honeypot_id}/", "active": False},
                {"label": "Edit YAML", "url": None, "active": True},
            ],
        },
    )
