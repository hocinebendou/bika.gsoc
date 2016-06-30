from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFPlone.utils import safe_unicode
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.Archetypes.references import HoldingReference
from plone.indexer import indexer
from bika.lims.interfaces import IStorageLocation
from zope.interface import implements
import sys


@indexer(IStorageLocation)
def get_parent_box_uid(instance):
    return instance.getParentBox().UID()

schema = BikaSchema.copy() + Schema((

    BooleanField(
        'IsOccupied',
        default=0,
        widget=BooleanWidget(visible=False),
    ),

    BooleanField(
        'IsReserved',
        default=0,
        widget=BooleanWidget(visible=False),
    ),

    StringField(
        'SampleUID',
        widget=StringWidget(visible=False),
    ),

    # ReferenceField('Product',
    #     vocabulary_display_path_bound = sys.maxint,
    #     allowed_types=('StockItem',),
    #     relationship='StockItemLocation',
    #     referenceClass=HoldingReference,
    #     widget=bika_ReferenceWidget(
    #         label=_("Stock Item"),
    #         catalog_name='bika_setup_catalog',
    #         showOn=True,
    #         description=_("Start typing to filter the list of available products."),
    #         ui_item='ProductTitle',
    #         search_fields=('ProductTitle', 'id',),
    #         colModel=[{'columnName': 'UID', 'hidden': True},
    #                   {'columnName': 'id', 'width': '35', 'label': _("Stock Item ID"), 'align': 'left'},
    #                   {'columnName': 'ProductTitle', 'width': '65', 'label': _('Product'), 'align': 'left'},
    #                   ],
    #     )),

    ReferenceField('Sample',
        vocabulary_display_path_bound=sys.maxint,
        allowed_types=('Aliquot', 'Biospecimen',),
        relationship='AliquotLocation',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
           label=_("Sample"),
           showOn=True,
           description=_("Start typing to filter the list of available samples."),
        )),

    ReferenceField(
        'ParentBox',
        required=1,
        allowed_types=('StorageManagement',),
        referenceClass=HoldingReference,
        relationship='StorageManagementLocation',
        widget=bika_ReferenceWidget(
            label=_('Box/Cane'),
            size=30,
            catalog_name='bika_setup_catalog',
            base_query={'inactive_state': 'active'},
            showOn=True,
        ),
    ),

    StringField(
        'Room',
        widget=StringWidget(visible=True),
    ),
    StringField(
        'StorageType',
        widget=StringWidget(visible=True),
    ),
    StringField(
        'Shelf',
        widget=StringWidget(visible=False),
    ),
    StringField(
        'Box',
        widget=StringWidget(visible=False),
    ),
    StringField(
        'Position',
        widget=StringWidget(visible=False),
    ),
    StringField(
        'LocationSampleID',
        widget=StringWidget(visible=False),
    ),
))
schema['title'].widget.label=_('Address')
schema['description'].widget.visible = True


class StorageLocation(BaseContent, HistoryAwareMixin):
    implements(IStorageLocation)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('title').get(self)).encode('utf-8')

registerType(StorageLocation, PROJECTNAME)

