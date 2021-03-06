from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from plone.app.layout.globals.interfaces import IViewView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from Products.Archetypes import PloneMessageFactory as _p
from bika.lims.interfaces import IStorageLocations
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from Products.CMFCore.utils import getToolByName
import json
import plone

class StorageLocationsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StorageLocationsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'StorageLocation',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                            {'url': 'createObject?type_name=StorageLocation',
                             'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Storage Locations"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/storagelocation_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Storage Location'),
                      'index':'sortable_title'},
            'Room': {'title': _('Room'),
                     'toggle': True},
            'Type': {'title': _('Storage Type'),
                     'toggle': True},
            'Hierarchy': {'title': _('Hierarchy'),
                          'toggle': True},
            'Sample': {'title': _('Sample'),
                          'toggle': True},
        }

        # ________________________________ #
        #    HOCINE ADD POSITION WORKFLOW  #
        # ________________________________ #
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active',
                               'sort_on': 'created',
                               'sort_order': 'ascending'},
             'transitions': [{'id':'deactivate'},
                             {'id': 'reserve'},
                             {'id': 'occupy'},],
             'columns': ['Title',
                         'Room',
                         'Type',
                         'Hierarchy',
                         'Sample',
                        ]},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Room',
                         'Type',
                         'Hierarchy',
                         'Sample',
                        ]},
            {'id': 'position_free',
             'title': _('Free'),
             'contentFilter': {'review_state': 'position_free',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'deactivate'},
                             {'id': 'reserve'},
                             {'id': 'occupy'}],
             'columns': ['Title',
                         'Room',
                         'Type',
                         'Hierarchy',
                         ]},
            {'id': 'position_reserved',
             'title': _('Reserved'),
             'contentFilter': {'review_state': 'position_reserved',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'deactivate'},
                             {'id': 'free'},
                             {'id': 'occupy'}],
             'columns': ['Title',
                         'Room',
                         'Type',
                         'Hierarchy',
                         ]},
            {'id': 'position_occupied',
             'title': _('Occupied'),
             'contentFilter': {'review_state': 'position_occupied',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'deactivate'},
                             {'id': 'free'},
                             {'id': 'reserve'},],
             'columns': ['Title',
                         'Room',
                         'Type',
                         'Hierarchy',
                         'Sample',
                         ]},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{'sort_on': 'created',
                              'sort_order': 'ascending'},
             'columns': ['Title',
                         'Room',
                         'Type',
                         'Hierarchy',
                         'Sample',
                        ]},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            items[x]['Room'] = obj.getRoom()
            items[x]['Type'] = obj.getStorageType()
            items[x]['Hierarchy'] = obj.getHierarchy()
            items[x]['Sample'] = obj.getSample() and obj.getSample().Title() or ''
            # if obj.aq_parent.portal_type == 'Client':
            #     items[x]['Owner'] = obj.aq_parent.Title()
            # else:
            #     items[x]['Owner'] = self.context.bika_setup.laboratory.Title()
        return items

schema = ATFolderSchema.copy()

class StorageLocations(ATFolder):
    implements(IStorageLocations)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(StorageLocations, PROJECTNAME)

class ajax_StorageLocations(BrowserView):
    """ The autocomplete data source for storage location selection widgets.
        Returns a JSON list of storage location titles.

        Request parameters:

        - term: the string which will be searched against all Storage Location
          titles.

        - _authenticator: The plone.protect authenticator.

    """

    def filter_list(self, items, searchterm):
        if searchterm and len(searchterm) < 3:
            # Items that start with A or AA
            res = [s.getObject()
                     for s in items
                     if s.title.lower().startswith(searchterm)]
            if not res:
                # or, items that contain A or AA
                res = [s.getObject()
                         for s in items
                         if s.title.lower().find(searchterm) > -1]
        else:
            # or, items that contain searchterm.
            res = [s.getObject()
                     for s in items
                     if s.title.lower().find(searchterm) > -1]
        return res

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        term = safe_unicode(self.request.get('term', '')).lower()
        if not term:
            return json.dumps([])

        client_items = lab_items = []

        # User (client) storage locations
        if self.context.portal_type == 'Client':
            client_path = self.context.getPhysicalPath()
            client_items = list(
                bsc(portal_type = "StorageLocation",
                    path = {"query": "/".join(client_path), "level": 0},
                    inactive_state = 'active',
                    sort_on='sortable_title'))

        # Global (lab) storage locations
        lab_path = \
                self.context.bika_setup.bika_storagelocations.getPhysicalPath()
        lab_items = list(
            bsc(portal_type = "StorageLocation",
                path = {"query": "/".join(lab_path), "level" : 0 },
                inactive_state = 'active',
                sort_on='sortable_title'))

        client_items = [callable(s.Title) and s.Title() or s.title
                 for s in self.filter_list(client_items, term)]
        lab_items = [callable(s.Title) and s.Title() or s.title
                 for s in self.filter_list(lab_items, term)]
        lab_items = ["%s: %s" % (_("Lab"), safe_unicode(i))
                     for i in lab_items]

        items = client_items + lab_items

        return json.dumps(items)
