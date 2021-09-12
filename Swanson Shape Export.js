//https://graphicdesign.stackexchange.com/questions/20905/looking-for-an-illustrator-script-to-export-without-anti-aliasing
function process(item){
    if (item.layers) {
        for (var i = 0; i < item.layers.length; i++) {
            if(item.layers[i].visible) process(item.layers[i]);
        }
    }
    if (item.groupItems) {
        for (var i = 0; i < item.groupItems.length; i++) {
            if(! item.groupItems[i].hidden) process(item.groupItems[i]);
        }
    }
    for (var i = 0; i < item.pageItems.length; i++) {
        if (item.pageItems[i].typename != 'GroupItem') {
            array.push(item.pageItems[i]);
        }
    }
}

function saveZones(name, regionType, fileName){
    var myDoc = app.activeDocument;
    var folder = activeDocument.path.fsName;
    var lvl = myDoc.name.slice(-5,-3);
    var exportPath  = folder+'/../'+regionType+'/';
    var exportOptions = new ExportOptionsPNG24();
    var type = ExportType.PNG24;
    exportOptions.artBoardClipping = true;
    exportOptions.antiAliasing = false;
    exportOptions.transparency = false;
    exportOptions.saveAsHTML = false;
    exportOptions.verticalScale = 600;
    exportOptions.horizontalScale = 600;

    var rasterizeOptions = new RasterizeOptions();
    rasterizeOptions.backgroundBlack = false;
    rasterizeOptions.clippingMask = false;
    rasterizeOptions.resolution = 432.0;
    rasterizeOptions.transparency = false;
    rasterizeOptions.convertSpotColors = true;
    rasterizeOptions.antiAliasingMethod = AntiAliasingMethod.None;

    var fileExport = new File(exportPath+'lvl'+lvl+'_'+fileName);
    var t = myDoc.layers.add();
    t.name = 'tmp '+name;
    var tmpGroup = t.groupItems.add();
    array = [];
    process(myDoc.layers.getByName(name));
    for (var i = array.length-1; i>=0; i--) {
        tmpSel = array[i].duplicate();
        tmpSel.moveToBeginning(tmpGroup);
    };
    tmpRast = myDoc.rasterize(tmpGroup, myDoc.artboardRect, rasterizeOptions);
    myDoc.exportFile( fileExport, type, exportOptions );
    tmpRast.remove();
    t.remove();
}


if (app.documents.length > 0) {

	if (app.activeDocument.selection.length < 1) {
		alert('Select a path');
	} else if (app.activeDocument.selection[0].area) {
		// Individual Items
		var objects =  app.activeDocument.selection;
	} else if (app.activeDocument.selection[0].pathItems) {
		// Group/Compound Shape
		var objects = app.activeDocument.selection[0].pathItems;
	} else {
		alert('Please select a path or group.');
	}

    var newRGBColor = new RGBColor();
    newRGBColor.red = 0;
    newRGBColor.green = 0;
    newRGBColor.blue = 0;
    // make all items hidden
    for (var i=0; i<objects.length; i++) {
        var item = objects[i];
        item.hidden = true;
        item.fillColor = newRGBColor; // just for testing
    }
    regionType = app.activeDocument.activeLayer.name
	// Collect info
	//var totalArea = 0;
	for (var i=0; i<objects.length; i++) {
		if (objects[i].area) {
			//var totalArea = totalArea + objects[i].area;
            objects[i].hidden = !objects[i].hidden;
            saveZones(app.activeDocument.activeLayer.name, regionType, objects[i].name)//
            //$.writeln('tacos'+i+'.png')
            objects[i].hidden = !objects[i].hidden;
		}
	}

}