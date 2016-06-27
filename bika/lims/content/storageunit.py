from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims import config
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IStorageUnit
from plone.app.folder.folder import ATFolder
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

import sys

schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((
    BooleanField('HasLevels',
        default=False,
        widget=BooleanWidget(visible=False),
    ),
    StringField('StorageUnitID',
        required = 1,
        searchable = True,
        validators = ('uniquefieldvalidator', 'standard_id_validator'),
        widget = StringWidget(
            label=_("Unit ID"),
            placeholder='eg: DNALab, RNALab...'
        ),
    ),
    StringField('Temperature',
        widget = StringWidget(
            label=_('Temperature'),
            description=_("Units can be specified in bika setup under Inventory."),
            input_class='numeric',
        ),
    ),
    ReferenceField('Department',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Department',),
        relationship = 'StorageUnitDepartment',
        vocabulary = 'getDepartments',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_('Department'),
            description=_('The laboratory department'),
        ),
    ),
    TextField('Address',
        default_output_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget(
            label = _('Address')),
    ),
    # FileField('StorageDocument',
    #     schemata = 'Details',
    #     widget=FileWidget(
    #         label = _('Instructions document')),
    # ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class StorageUnit(ATFolder):
    security = ClassSecurityInfo()
    implements(IStorageUnit)
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getDepartments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        result = []
        for r in bsc(portal_type='Department',
                     inactive_state='active'):
            result.append((r.UID, r.Title))
        return DisplayList(result)

    def getDepartmentTitle(self):
        return self.getDepartment() and self.getDepartment().Title() or ''


registerType(StorageUnit, config.PROJECTNAME)
