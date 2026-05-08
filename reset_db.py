from django.db import transaction
from society.models import *
from statutory.models import *

def run():
    with transaction.atomic():

        print("Deleting Bylaws runtime...")
        RegistrarSubmission.objects.all().delete()
        SocietyBylaws.objects.all().delete()
        BylawDecision.objects.all().delete()

        print("Deleting Share Certificates...")
        ShareCertificate.objects.all().delete()
        SocietyLegalDocument.objects.all().delete()
        
        print("Deleting Financial...")
        LedgerEntry.objects.all().delete()
        TransactionRule.objects.all().delete()
        AccountingPeriod.objects.all().delete()
        ChartOfAccount.objects.all().delete()

        print("Deleting Structure...")
        FlatMaintenanceBill.objects.all().delete()
        MaintenanceAccount.objects.all().delete()
        FlatOwnership.objects.all().delete()
        FlatOccupancy.objects.all().delete()
        Flat.objects.all().delete()
        Floor.objects.all().delete()
        Wing.objects.all().delete()

        print("Deleting Governance...")
        CommitteeMembership.objects.all().delete()
        Committee.objects.all().delete()

        print("Deleting Membership...")
        SocietyMember.objects.all().delete()

        print("Deleting Society...")
        Society.objects.all().delete()

        print("Deleting Persons...")
        Person.objects.all().delete()

        print("✅ RESET COMPLETE")

run()
