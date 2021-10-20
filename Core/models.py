from django.db import models


# Create your models here.
class ICD10CodeCategory(models.Model):
    def __str__(self):
        return '%s' %self.description

    hdr_local_id = models.IntegerField()
    description = models.CharField(max_length=255)

    class Meta:
        db_table="ICD10CodeCategories"
        verbose_name_plural = "ICD10 Code Categories"


class ICD10CodeSubCategory(models.Model):
    def __str__(self):
        return '%s' % self.description

    hdr_local_id = models.IntegerField()
    category = models.ForeignKey(ICD10CodeCategory,related_name='sub_category', on_delete=models.DO_NOTHING, null=True, blank=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "ICD10CodeSubCategories"
        verbose_name_plural = "ICD10 Code Sub Categories"


class ICD10Code(models.Model):
    def __str__(self):
        return '%s' %self.description

    hdr_local_id = models.IntegerField()
    sub_category = models.ForeignKey(ICD10CodeSubCategory,related_name='code', on_delete=models.DO_NOTHING, null=True, blank=True)
    code = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    class Meta:
        db_table="ICD10Codes"
        verbose_name_plural = "ICD10 Codes"


class ICD10SubCode(models.Model):
    def __str__(self):
        return '%d' %self.id

    hdr_local_id = models.IntegerField()
    code = models.ForeignKey(ICD10Code,related_name='sub_code',on_delete=models.DO_NOTHING, null=True, blank=True)
    sub_code = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    class Meta:
        db_table="ICD10SubCodes"
        verbose_name_plural = "ICD10 SubCodes"


class CPTCodeCategory(models.Model):
    def __str__(self):
        return '%d' %self.id

    hdr_local_id = models.IntegerField()
    description = models.CharField(max_length=255)

    class Meta:
        db_table="CPTCodeCategories"
        verbose_name_plural = "CPT Code Categories"


class CPTCodeSubCategory(models.Model):
    def __str__(self):
        return '%d' % self.id

    hdr_local_id = models.IntegerField()
    category = models.ForeignKey(CPTCodeCategory, related_name='sub_category',on_delete=models.DO_NOTHING, null=True, blank=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "CPTCodeSubCategories"
        verbose_name_plural = "CPT Code Sub Categories"


class CPTCode(models.Model):
    def __str__(self):
        return '%d' %self.id

    hdr_local_id = models.IntegerField()
    sub_category = models.ForeignKey(CPTCodeSubCategory,related_name='code', on_delete=models.DO_NOTHING, null=True, blank=True)
    code = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    local_code = models.CharField(max_length=255, default=0)

    class Meta:
        db_table = "CPTCodes"
        verbose_name = "CPT Code"


class Query(models.Model):
    def __str__(self):
        return '%d' %self.id

    ServicesReceived = 'SVCREC'
    DeathByDiseaseCaseAtFacility = 'DDC'
    DeathByDiseaseCaseNotAtFacility = 'DDCOUT'
    RevenueReceived = 'REV'
    BedOccupancy = 'BEDOCC'

    MESSAGE_TYPE_CHOICES = (
        (ServicesReceived, 'SVCREC'),
        (DeathByDiseaseCaseAtFacility, 'DDC'),
        (DeathByDiseaseCaseNotAtFacility, 'DDCOUT'),
        (RevenueReceived, 'REV'),
        (BedOccupancy, 'BEDOCC'),
    )

    message_type = models.CharField(max_length=100, choices=MESSAGE_TYPE_CHOICES)
    sql_statement = models.TextField()
    condition_field = models.CharField(max_length=255)
    date_format = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "Queries"
        verbose_name_plural = "Queries"


