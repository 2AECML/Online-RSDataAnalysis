// calinfo.js


// 服务端的地址
var serverAddress = window.location.protocol + "//" + window.location.hostname

// GeoServer的端口号
var geoServerPort = 8080

// 计算信息
var calInfo = calInfo || {};
calInfo.calculateTypes = new Set([]);
calInfo.imageType = '';
calInfo.time = '';
calInfo.coordinates = [];

// 当前图层
var curLayerName = '';

// 结果图层的ID
var resultID = 0;

// 结果图层的映射
var resultMap = new Map();

// 绘制源
const drawSource = new ol.source.Vector();
var draw = null; // 当前的绘制交互
const drawLayer = new ol.layer.Vector({
    source: drawSource,
    zIndex: 100
});

