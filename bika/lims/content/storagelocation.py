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
        required=1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types=('Stock Item',),
        relationship='StockItemLocation',
        referenceClass=HoldingReference,
        widget=bika_ReferenceWidget(
            label = _("Stock Item"),
            catalog_name='bika_setup_catalog',
            showOn=False,
            description=_("Start typing to filter the list of available products."),
        )),

    StringField(
        'Room',
        widget=StringWidget(visible=False),
    ),
    StringField(
        'StorageType',
        widget=StringWidget(visible=False),
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

    def getHierarchy(self, char='>'):
        ancestors = []
        ancestor = self
        # portal_types = [o.portal_type for o in ancestor.aq_chain if hasattr(o, 'portal_type')]
        # if not 'StorageUnit' not in portal_types:
        #     return ''

        portal_types = []
        for o in ancestor.aq_chain:
            if hasattr(o, 'portal_type'):
                portal_types.append(o.portal_type)

        if not 'StorageUnit' in portal_types:
            return ''

        for obj in ancestor.aq_chain:
            ancestors.append(obj.getId())
            if obj.portal_type == 'StorageUnit':
                break

        return char.join(reversed(ancestors))

    def getChain(self):
        chain = []
        ancestor = self

        portal_types = []
        for o in ancestor.aq_chain:
            if hasattr(o, 'portal_type'):
                portal_types.append(o.portal_type)

        if not 'StorageUnit' in portal_types:
            return ''

        for obj in ancestor.aq_chain:
            chain.append(obj)
            if obj.portal_type == 'StorageUnit':
                break

        return chain

registerType(StorageLocation, PROJECTNAME)

