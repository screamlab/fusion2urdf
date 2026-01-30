# -*- coding: utf-8 -*-
"""
Created on Sun May 12 19:15:34 2019

@author: syuntoku
"""

import adsk, adsk.core, adsk.fusion
import os.path, re
from xml.etree import ElementTree
from xml.dom import minidom
# from distutils.dir_util import copy_tree
from shutil import copytree
import fileinput
import sys

def copy_occs(root):    
    """    
    duplicate all the components
    Original components keep their names, copied components are prefixed with 'exported_'
    """    
    def copy_body(allOccs, occs):
        """    
        copy the old occs to new component
        """
        
        bodies = occs.bRepBodies
        transform = adsk.core.Matrix3D.create()
        
        # Create new components from occs
        new_occs = allOccs.addNewComponent(transform)  # this create new occs
        # Name the copied component with 'exported_' prefix
        # Use the component name for base_link to avoid base_link_1 STL naming
        occs_name = re.sub('[ :()]', '_', occs.name)
        component_name = re.sub('[ :()]', '_', occs.component.name)
        if component_name == 'base_link':
            new_occs.component.name = 'exported_base_link'
        else:
            new_occs.component.name = 'exported_' + occs_name
        new_occs = allOccs.item((allOccs.count-1))
        
        for i in range(bodies.count):
            body = bodies.item(i)
            body.copyToComponent(new_occs)
    
    allOccs = root.occurrences
    copy_list = [allOccs.item(i) for i in range(allOccs.count)]
    
    # Copy bodies from original components (keep original names)
    for occs in copy_list:
        if occs.bRepBodies.count > 0:
            copy_body(allOccs, occs)


def cleanup_copied_components(root):
    """
    Remove all copied components that were created during STL export
    Keep only the original components (those without 'exported_' prefix)
    """
    allOccs = root.occurrences
    components_to_remove = []
    
    # Collect all occurrences and identify which ones are copied
    occs_list = [allOccs.item(i) for i in range(allOccs.count)]
    
    for occs in occs_list:
        comp_name = occs.component.name
        # Remove components with 'exported_' prefix (these are the copies)
        if comp_name.startswith('exported_'):
            components_to_remove.append(occs)
    
    # Remove copied components in reverse order to avoid index issues
    for occs in reversed(components_to_remove):
        try:
            occs.deleteMe()
        except Exception as e:
            print(f"Failed to remove component {occs.component.name}: {str(e)}")


def export_stl(design, save_dir, components):  
    """
    export stl files into "save_dir/"
    Export only from copied components (those with 'exported_' prefix)
    
    Parameters
    ----------
    design: adsk.fusion.Design.cast(product)
    save_dir: str
        directory path to save
    components: design.allComponents
    """
          
    # create a single exportManager instance
    exportMgr = design.exportManager
    # get the script location
    try: os.mkdir(save_dir + '/meshes')
    except: pass
    scriptDir = save_dir + '/meshes'  
    # export the occurrence one by one in the component to a specified file
    for component in components:
        allOccus = component.allOccurrences
        for occ in allOccus:
            # Only export copied components (those with 'exported_' prefix)
            if occ.component.name.startswith('exported_'):
                try:
                    # Remove the 'exported_' prefix when saving STL filename
                    stl_name = occ.component.name.replace('exported_', '')
                    print(stl_name)
                    fileName = scriptDir + "/" + stl_name              
                    # create stl exportOptions
                    stlExportOptions = exportMgr.createSTLExportOptions(occ, fileName)
                    stlExportOptions.sendToPrintUtility = False
                    stlExportOptions.isBinaryFormat = True
                    # options are .MeshRefinementLow .MeshRefinementMedium .MeshRefinementHigh
                    stlExportOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementLow
                    exportMgr.execute(stlExportOptions)
                except:
                    print('Component ' + occ.component.name + ' has something wrong.')
                

def file_dialog(ui):     
    """
    display the dialog to save the file
    """
    # Set styles of folder dialog.
    folderDlg = ui.createFolderDialog()
    folderDlg.title = 'Fusion Folder Dialog' 
    
    # Show folder dialog
    dlgResult = folderDlg.showDialog()
    if dlgResult == adsk.core.DialogResults.DialogOK:
        return folderDlg.folder
    return False


def origin2center_of_mass(inertia, center_of_mass, mass):
    """
    convert the moment of the inertia about the world coordinate into 
    that about center of mass coordinate


    Parameters
    ----------
    moment of inertia about the world coordinate:  [xx, yy, zz, xy, yz, xz]
    center_of_mass: [x, y, z]
    
    
    Returns
    ----------
    moment of inertia about center of mass : [xx, yy, zz, xy, yz, xz]
    """
    x = center_of_mass[0]
    y = center_of_mass[1]
    z = center_of_mass[2]
    translation_matrix = [y**2+z**2, x**2+z**2, x**2+y**2,
                         -x*y, -y*z, -x*z]
    return [ round(i - mass*t, 6) for i, t in zip(inertia, translation_matrix)]


def prettify(elem):
    """
    Return a pretty-printed XML string for the Element.
    Parameters
    ----------
    elem : xml.etree.ElementTree.Element
    
    
    Returns
    ----------
    pretified xml : str
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def copy_package(save_dir, package_dir):
    try: os.mkdir(save_dir + '/launch')
    except: pass 
    try: os.mkdir(save_dir + '/urdf')
    except: pass 
    # copy_tree(package_dir, save_dir)
    copytree(package_dir, save_dir, dirs_exist_ok=True)

def update_cmakelists(save_dir, package_name):
    file_name = save_dir + '/CMakeLists.txt'

    for line in fileinput.input(file_name, inplace=True):
        if 'project(fusion2urdf)' in line:
            sys.stdout.write("project(" + package_name + ")\n")
        else:
            sys.stdout.write(line)

def update_package_xml(save_dir, package_name):
    file_name = save_dir + '/package.xml'

    for line in fileinput.input(file_name, inplace=True):
        if '<name>' in line:
            sys.stdout.write("  <name>" + package_name + "</name>\n")
        elif '<description>' in line:
            sys.stdout.write("<description>The " + package_name + " package</description>\n")
        else:
            sys.stdout.write(line)
        
