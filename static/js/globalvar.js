// calinfo.js

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

