#Author-syuntoku14
#Description-Clean up copied components created by URDF Exporter

import adsk, adsk.core, adsk.fusion, traceback
import re
from .utils import utils

def run(context):
    ui = None
    
    try:
        # Initialize
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        title = 'URDF Component Cleanup'
        
        if not design:
            ui.messageBox('No active Fusion design', title)
            return

        root = design.rootComponent
        
        # Count components to be cleaned
        allOccs = root.occurrences
        copied_components = []
        original_components = []
        
        for i in range(allOccs.count):
            occs = allOccs.item(i)
            if occs.component.name == 'old_component':
                original_components.append(occs)
            elif any(keyword in occs.component.name.lower() for keyword in ['copy', 'temp_', 'duplicate']):
                copied_components.append(occs)
        
        if len(copied_components) == 0 and len(original_components) == 0:
            ui.messageBox('No copied components found to clean up.', title)
            return
        
        # Confirm cleanup
        cleanup_msg = f'Found {len(copied_components)} copied components and {len(original_components)} renamed original components.\n\n'
        cleanup_msg += 'Do you want to clean them up?\n\n'
        cleanup_msg += 'This will:\n'
        cleanup_msg += '• Remove copied components\n'
        cleanup_msg += '• Restore original component names\n'
        
        result = ui.messageBox(
            cleanup_msg,
            title,
            adsk.core.MessageBoxButtonTypes.YesNoButtonType,
            adsk.core.MessageBoxIconTypes.QuestionIconType
        )
        
        if result != adsk.core.DialogResults.DialogYes:
            ui.messageBox('Cleanup canceled.', title)
            return
        
        # Perform cleanup
        utils.cleanup_copied_components(root)
        
        ui.messageBox(f'Successfully cleaned up {len(copied_components)} copied components and restored {len(original_components)} original component names.', title)
        
    except:
        if ui:
            ui.messageBox('Failed to clean up components:\n{}'.format(traceback.format_exc()), 'URDF Component Cleanup')
