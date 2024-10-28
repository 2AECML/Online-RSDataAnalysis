// map.js


// 创建地图
var map = new ol.Map({
    view: new ol.View({
        center: ol.proj.fromLonLat([116.397, 39.907]), // 北京
        zoom: 8
    })
});


$(document).ready(function () {
    map.setTarget("MapContainer");
});

