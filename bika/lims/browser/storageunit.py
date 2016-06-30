from bika.sanbi.controlpanel.bika_storageinventories import StorageInventoriesView
from bika.sanbi.controlpanel.bika_storagemanagements import StorageManagementsView
from bika.sanbi import bikaMessageFactory as _


class StorageUnitInventoryView(StorageInventoriesView):
    def __init__(self, context, request):
        super(StorageUnitInventoryView, self).__init__(context, request)
        self.contentFilter['getUnitID'] = context.getId()
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=StorageInventory',
                                 'icon': '++resource++bika.lims.images/add.png'}}

class StorageUnitManagementView(StorageManagementsView):
    def __init__(self, context, request):
        super(StorageUnitManagementView, self).__init__(context, request)