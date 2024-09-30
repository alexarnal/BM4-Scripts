/*
 * Illustrator Export Script for Neuroscience Imaging Data
 * 
 * Description:
 * This script automates the export of neuroanatomical data from Adobe Illustrator files
 * to various image formats (PNG and SVG) for further analysis and visualization in 
 * neuroscience research. It is designed to process multilayered Illustrator documents 
 * containing different types of neuronal structures.
 * 
 * Functionality:
 * 1. Exports fiber data as PNG8 images
 * 2. Exports cell body data as SVG files
 * 3. Exports apposition data as SVG files
 * 4. Processes multiple layers and sublayers based on specified peptide markers
 * 5. Maintains original layer structure and visibility
 * 6. Reads project-specific details from an external CSV file
 * 
 * Usage:
 * 1. Open the target Illustrator file
 * 2. Ensure the `projectDetails.csv` file is present in the `scripts` folder
 * 3. Run the script from within Adobe Illustrator
 * 
 * Requirements:
 * - Adobe Illustrator CS6 or later
 * - Properly structured Illustrator file with layers named according to peptide markers
 * - `projectDetails.csv` file in the `scripts` folder containing project-specific information
 * 
 * Output Structure:
 * The script generates the following folder structure relative to the Illustrator file:
 * - ../fibers/raw/: Contains exported PNG8 images of fiber data
 * - ../cells/raw/: Contains exported SVG files of cell body data
 * - ../appositions/raw/: Contains exported SVG files of apposition data
 * 
 * File Naming:
 * Exported files are named using the following convention:
 * [first 6 characters of layer name]_[peptide marker]_lvl[level number]_[layer index].[extension]
 * 
 * Notes:
 * - The script assumes specific layer naming conventions and structure
 * - Fiber data is exported with black stroke color and 0.3 pt width for consistency
 * - SVG exports use optimized settings for web compatibility
 * 
 * Useful links (not my own):
 * - adobe scripting tutorial: https://www.youtube.com/watch?v=EGdgrP7azUQ
 * - export svg spects: https://community.adobe.com/t5/illustrator/svg-export-only-visible-layers/m-p/8820328
 *
 * Author: Alexandro Arnal
 * Version: 1.0
 * Date: Sept 30, 2024
 * 
 * This script is part of the data processing pipeline for Navarro et al. 2024.
*/

//Function definitions
function exportFileToPNG8(dest) {
    if (app.documents.length > 0) {
      var exportOptions = new ExportOptionsPNG8();
      exportOptions.antiAliasing = true;
      exportOptions.artBoardClipping = true;
      exportOptions.transparency = false;
      exportOptions.matte = true;
      exportOptions.verticalScale = 600;
      exportOptions.horizontalScale = 600;
      
      var type = ExportType.PNG8;
      var fileSpec = new File(dest);
  
      app.activeDocument.exportFile(fileSpec, type, exportOptions);
    }
}
function exportFileToSVG(dest) {
    if (app.documents.length > 0) {
      var exportOptions = new ExportOptionsWebOptimizedSVG();
      exportOptions.saveMultipleArtboards = true;
      exportOptions.coordinatePrecision = 4;
      exportOptions.fontType = SVGFontType.OUTLINEFONT;
      exportOptions.svgMinify = true;
      exportOptions.svgId = SVGIdType.SVGIDREGULAR;
      var type = ExportType.WOSVG;
      var fileSpec = new File(dest);
  
      app.activeDocument.exportFile(fileSpec, type, exportOptions);
    }
}

function getProjectDetail(folder, type) {
    var testtextfile = File(folder.slice(0,-8)+"/scripts/projectDetails.csv"); // expects folder name to be "ai files" or any 8 character string
    testtextfile.encoding = 'UTF8'; // set to 'UTF8' or 'UTF-8'
    testtextfile.open("r");
    var fileContentsString = testtextfile.readln();
    while (fileContentsString.slice(0,type.length) != type){
        fileContentsString = testtextfile.readln();
        if (fileContentsString.length == 0){
            alert("No matching project detail found");
            testtextfile.close();
            return false;
        }
    }
    testtextfile.close();
    array = fileContentsString.split(" ").join("").split(",")
    return array.slice(1,array.length)
}

function main() {
    var myDoc = app.activeDocument;
    var folder = activeDocument.path.fsName;
    var lvl = myDoc.name.slice(-5,-3);
    var layerLen = myDoc.layers.length;
    var pep = getProjectDetail(folder, "markers")
    if (pep == false){return;}
    var newRGBColor = new RGBColor();
    newRGBColor.red = 0;
    newRGBColor.green = 0;
    newRGBColor.blue = 0;
    
    //Hide everything
    var skip = true
    for (var i = 0; i < layerLen; i++){
        var layer_1 = myDoc.layers[i];
        layer_1.visible = false;
        for (var p = 0; p < pep.length; p++)
            if (layer_1.name.indexOf(pep[p])>0){
                skip = false;
            }
        //Skip layers that do not contain the peptide names
        if (skip == true) {continue;}
        else {skip = true;}
    
        for (var j = 0; j< layer_1.layers.length; j++){
            var layer_2 = layer_1.layers[j];
            layer_2.visible = false;
            for (var k = 0; k<layer_2.layers.length; k++){
                layer_2.layers[k].visible = false;
            }
        }
    }
    
    //Export data layers individually
    for (var i = 0; i < layerLen; i++){
        var layer_1 = myDoc.layers[i];
        for (var p = 0; p< pep.length; p++){
            if (layer_1.name.indexOf(pep[p])<0){
                continue;
            }
            var layer_2 = layer_1.layers.getByName(pep[p])
            for (var d = 0; d<layer_2.layers.length; d++){
                if (layer_2.layers[d].name == 'Fibers'){
                    layer_1.visible = !layer_1.visible;
                    layer_2.visible = !layer_2.visible;
                    layer_2.layers[d].visible = !layer_2.layers[d].visible; 
                    for(c=0;c<layer_2.layers[d].pathItems.length;c++) { 
                        layer_2.layers[d].pathItems[c].strokeColor = newRGBColor;
                        layer_2.layers[d].pathItems[c].strokeWidth = 0.3; 
                    } 
                    exportFileToPNG8(folder+'/../fibers/raw/'+layer_1.name.substr(0,6)+'_'+pep[p]+'_lvl'+lvl+'_'+i+'.png');
                    layer_1.visible = !layer_1.visible;
                    layer_2.visible = !layer_2.visible;
                    layer_2.layers[d].visible = !layer_2.layers[d].visible;
                }
                if (layer_2.layers[d].name == 'Cell Bodies'){
                    layer_1.visible = !layer_1.visible;
                    layer_2.visible = !layer_2.visible;
                    layer_2.layers[d].visible = !layer_2.layers[d].visible ;
                    exportFileToSVG(folder+'/../cells/raw/'+layer_1.name.substr(0,6)+'_'+pep[p]+'_lvl'+lvl+'_'+i+'.png');
                    layer_1.visible = !layer_1.visible;
                    layer_2.visible = !layer_2.visible;
                    layer_2.layers[d].visible = !layer_2.layers[d].visible;
                }
                if (layer_2.layers[d].name == 'Appositions'){
                    layer_1.visible = !layer_1.visible;
                    layer_2.visible = !layer_2.visible;
                    layer_2.layers[d].visible = !layer_2.layers[d].visible;
                    exportFileToSVG(folder+'/../appositions/raw/'+layer_1.name.substr(0,6)+'_'+pep[p]+'_lvl'+lvl+'_'+i+'.png');
                    layer_1.visible = !layer_1.visible;
                    layer_2.visible = !layer_2.visible;
                    layer_2.layers[d].visible = !layer_2.layers[d].visible;
                }
            }
        }
    }
    
    //Unhide everything
    var skip = true
    for (var i = 0; i < layerLen; i++){
        var layer_1 = myDoc.layers[i];
        layer_1.visible = true;
        for (var p = 0; p < pep.length; p++)
            if (layer_1.name.indexOf(pep[p])>0){
                skip = false;
            }
    
        if (skip == true) {continue;}
        else {skip = true;}
    
        for (var j = 0; j< layer_1.layers.length; j++){
            var layer_2 = layer_1.layers[j];
            layer_2.visible = true;
            for (var k = 0; k<layer_2.layers.length; k++){
                layer_2.layers[k].visible = true;
            }
        }
    }
}

main()
