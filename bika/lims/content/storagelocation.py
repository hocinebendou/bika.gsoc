from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFPlone.utils import safe_unicode
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from Products.Archetypes.references import HoldingReference
import sys

schema = BikaSchema.copy() + Schema((

    BooleanField(
        'IsOccupied',
        default=0,
        widget=BooleanWidget(visible=False),
    ),
    StringField(
        'StockItemID',
        widget=StringWidget(visible=False),
    ),
    ReferenceField('Product',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types=('StockItem',),
        relationship='StockItemLocation',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label=_("Stock Item"),
            catalog_name='bika_setup_catalog',
            showOn=True,
            description=_("Start typing to filter the list of available products."),
            ui_item='ProductTitle',
            search_fields=('ProductTitle', 'StockItemID',),
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'StockItemID', 'width': '35', 'label': _("Stock Item ID"), 'align': 'left'},
                      {'columnName': 'ProductTitle', 'width': '65', 'label': _('Product'), 'align': 'left'},
                      ],
        )),

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
))
schema['title'].widget.label=_('Address')
schema['description'].widget.visible = True


class StorageLocation(BaseContent, HistoryAwareMixin):
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

