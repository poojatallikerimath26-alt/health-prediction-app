from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from .forms import PatientRecordForm
from .models import PatientRecord
from .ml.predictor import generate_remarks


def patient_list(request):
    """READ: show every patient record, most recently updated first."""
    records = PatientRecord.objects.all()
    return render(request, "patients/patient_list.html", {"records": records})


def patient_create(request):
    """CREATE: add a new patient record and auto-generate its remarks."""
    if request.method == "POST":
        form = PatientRecordForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.remarks = generate_remarks(
                patient.glucose, patient.haemoglobin, patient.cholesterol
            )
            patient.save()
            messages.success(request, f"Record for {patient.full_name} created and analysed.")
            return redirect("patient_list")
    else:
        form = PatientRecordForm()
    return render(request, "patients/patient_form.html", {"form": form, "mode": "create"})


def patient_update(request, pk):
    """UPDATE: edit an existing record and re-run the prediction."""
    patient = get_object_or_404(PatientRecord, pk=pk)
    if request.method == "POST":
        form = PatientRecordForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.remarks = generate_remarks(
                patient.glucose, patient.haemoglobin, patient.cholesterol
            )
            patient.save()
            messages.success(request, f"Record for {patient.full_name} updated and re-analysed.")
            return redirect("patient_list")
    else:
        form = PatientRecordForm(instance=patient)
    return render(request, "patients/patient_form.html", {"form": form, "mode": "edit", "patient": patient})


def patient_delete(request, pk):
    """DELETE: remove a record after confirmation."""
    patient = get_object_or_404(PatientRecord, pk=pk)
    if request.method == "POST":
        name = patient.full_name
        patient.delete()
        messages.success(request, f"Record for {name} deleted.")
        return redirect("patient_list")
    return render(request, "patients/patient_confirm_delete.html", {"patient": patient})
