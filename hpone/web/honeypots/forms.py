from django import forms


class HoneypotYamlForm(forms.Form):
    content = forms.CharField(
        label="YAML",
        widget=forms.Textarea(
            attrs={
                "rows": 24,
                "class": "w-full rounded-xl border border-slate-800 bg-slate-950/70 p-4 font-mono text-xs text-slate-100 focus:border-emerald-400 focus:outline-none",
            }
        ),
    )
