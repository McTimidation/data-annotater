from django.shortcuts import get_object_or_404, redirect, render

from .forms import CSVUploadForm, RetailRowAnnotateForm
from .models import RetailRow
from .services import ingest_csv


def upload(request):

    stats = None

    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data["csv_file"]
            stats = ingest_csv(uploaded)
            form = CSVUploadForm()
    else:
        form = CSVUploadForm()

    return render(request, "data_annotater/upload.html", {"form": form, "stats": stats})


def retail_list(request):

    rows = (
        RetailRow.objects
        .filter(segment__isnull=True)
        .order_by("country", "merchant", "sku")
    )

    return render(request, "data_annotater/list.html", {"rows": rows})


def edit(request, pk: int):

    row = get_object_or_404(RetailRow, pk=pk)

    if request.method == "POST":
        form = RetailRowAnnotateForm(request.POST, instance=row)
        if form.is_valid():
            form.save()
            return redirect("list")
    else:
        form = RetailRowAnnotateForm(instance=row)

    return render(request, "data_annotater/edit.html", {"row": row, "form": form})

