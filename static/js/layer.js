// layer.js


const provincialLayer = new ol.layer.Tile({
    source: new ol.source.TileWMS({
        url: `${serverAddress}:${geoServerPort}/geoserver/wms`,
        params: {
            'LAYERS': 'local:省级',
            'TILED': true
        },
        serverType: 'geoserver',
        transition: 0
    }),
    zIndex: 50
});


const prefecturalLayer = new ol.layer.Tile({
    source: new ol.source.TileWMS({
        url: `${serverAddress}:${geoServerPort}/geoserver/wms`,
        params: {
            'LAYERS': 'local:地级',
            'TILED': true
        },
        serverType: 'geoserver',
        transition: 0
    }),
    zIndex: 50
});


const countyLayer = new ol.layer.Tile({
    source: new ol.source.TileWMS({
        url: `${serverAddress}:${geoServerPort}/geoserver/wms`,
        params: {
            'LAYERS': 'local:县级',
            'TILED': true
        },
        serverType: 'geoserver',
        transition: 0
    }),
    zIndex: 50
});


const imageLayer = new ol.layer.Tile({
    source: new ol.source.XYZ({
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    }),
    zIndex: 0
});


var remoteSource = new ol.source.TileWMS({
    url: `${serverAddress}:${geoServerPort}/geoserver/wms`,
    params: {
        'TILED': true
    },
    serverType: 'geoserver'
});


const remoteLayer = new ol.layer.Tile({
    source: remoteSource,
    zIndex: 5,
    opacity: 0.85
});


$(document).ready(function () {

    initAvailableDateAndImages();

    setupLayerToggle();

    $("#ImageLayer").click();

});


function initAvailableDateAndImages() {
    const imageTypes = ['Landsat', 'Sentinel', 'MODIS'];
    imageTypes.forEach(type => {
        $.ajax({
            type: "POST",
            url: "/get_available_dates",
            contentType: "application/json",
            data: JSON.stringify({
                imageType: type
            }),
            dataType: "json",
            success: function (response) {
                const dateArray = response.dates;
                dateArray.forEach(date => {
                    // console.log(date);
                    const divItem = $('<div>', {
                        id: `${type}-${date.year}-${date.month}`,
                        class: 'band-header'
                    }).append(
                        `${date.year}-${date.month}`
                    );
                    if (type === 'Landsat') {
                        $("#RemoteLayerList-Landsat8").append(divItem);
                    } else if (type === 'Sentinel') {
                        $("#RemoteLayerList-Sentinel-2").append(divItem);
                    } else if (type === 'MODIS') {
                        $("#RemoteLayerList-MODIS").append(divItem);
                    }
                    getAvailableImages(type, date);
                });
            },
            error: function (error) {
                console.error('Error:', error);
            }
        });
    });
}


function getAvailableImages(imageType, date) {
    $.ajax({
        type: "POST",
        url: "/get_available_images",
        contentType: "application/json",
        data: JSON.stringify({
            imageType: imageType,
            date: date
        }),
        dataType: "json",
        success: function (response) {
            // console.log(response);
            const images = response.images;
            if (images.length) {
                const ulitem = $('<ul>', {
                    id: `${imageType}-${date.year}-${date.month}-list`,
                    class: 'band-list'
                });
                const targetItem = $(`#${imageType}-${date.year}-${date.month}`);
                targetItem.append(ulitem);

                for (const image of images) {
                    const listItemText = image;
                    const listItem = $('<li>', {
                        id: `${listItemText}`,
                        style: 'display: none'
                    });
                    listItem.append(listItemText);
                    ulitem.append(listItem);
                }
            }
        },
        error: function (error) {
            console.error('Error:', error);
        }
    });
}


function setupLayerToggle() {
    $('.nav-list').on('click', 'li', function () {
        var id = $(this).attr('id');

        console.log(id)

        if (/^ProvincialLayer|PrefecturalLayer|CountyLayer|ImageLayer$/.test(id)) {
            // 处理图层开关
            var layerMap = {
                "ProvincialLayer": provincialLayer,
                "PrefecturalLayer": prefecturalLayer,
                "CountyLayer": countyLayer,
                "ImageLayer": imageLayer
            };
            toggleLayer(layerMap[id]);
        }
        else if (/^LAND*|SENT*|MODS*/.test(id)) {
            // 处理遥感图层
            map.removeLayer(remoteLayer);
            if (id === curLayerName) {
                curLayerName = '';
                remoteSource.updateParams({ 'LAYERS': '' });
                calInfo.imageType = '';
                calInfo.time = '';
            }
            else {
                curLayerName = id;
                remoteSource.updateParams({ 'LAYERS': 'local:' + curLayerName });
                map.addLayer(remoteLayer);
                console.log('切换遥感图层:', curLayerName);
                calInfo.imageType = 'Landsat';
                calInfo.time = curLayerName.split('_')[1];
            }
        }
        else if (/^NDWI|NWI|AWEInsh|AWEIsh|WI2015|MBWI|NDMBWI|GRN-WI$/.test(id)) {
            // 处理选择功能
            if (calInfo.calculateTypes.has(id)) {
                calInfo.calculateTypes.delete(id);
            }
            else {
                calInfo.calculateTypes.add(id);
            }
            startSelection();
        }
        else if (/^ResultItem*/.test(id)) {
            // 处理结果项点击事件
            const layer = getResultLayerByID(id.split('-')[1]);
            toggleLayer(layer);
        }
    });
}


function toggleLayer(layer) {
    map.getLayers().getArray().includes(layer) ? map.removeLayer(layer) : map.addLayer(layer);
}


function getResultLayerByID(id) {
    return resultMap.get(Number(id));
}

