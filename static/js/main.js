
// 定义全局变量
var calInfo = calInfo || {};
calInfo.calculateTypes = new Set([]);
calInfo.imageType = '';
calInfo.areaCode = '';
calInfo.time = '';
calInfo.coordinates = [];

let curLayerName = '';

// 创建地图
var map = new ol.Map({
    view: new ol.View({
        center: ol.proj.fromLonLat([116.397, 39.907]), // 北京
        zoom: 8
    })
});


const provincialLayer = new ol.layer.Tile({
    source: new ol.source.TileWMS({
        url: 'http://localhost:8080/geoserver/wms',
        params: {
            'LAYERS': 'local:LAND_202311_RGB',
            // 'STYLES': 'local:TrueColor',
            'TILED': true
        },
        serverType: 'geoserver',
        transition: 0
    }),
    zIndex: 50
});


const prefecturalLayer = new ol.layer.Tile({
    source: new ol.source.TileWMS({
        url: 'http://localhost:8080/geoserver/wms',
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
        url: 'http://localhost:8080/geoserver/wms',
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
    url: 'http://localhost:8080/geoserver/wms',
    params: {
        'STYLES': 'TrueColor(Landsat)',
        'TILED': true
    },
    serverType: 'geoserver',
})


const remoteLayer = new ol.layer.Tile({
    source: remoteSource,
    zIndex: 5
});


$(document).ready(function () {

    map.setTarget("MapContainer");

    getAvailableImages();

    $('.nav-list').on('click', 'li', function () {
        var id = $(this).attr('id');

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
        else if (/^Landsat8*/.test(id)) {
            // 处理遥感图层
            // resetRemoteLayer(id);

            map.removeLayer(remoteLayer);
            if (id === curLayerName) {
                curLayerName = '';
                remoteSource.updateParams({ 'LAYERS': '' });
            }
            else {
                curLayerName = id;
                initAvailableDates();
                // remoteSource.updateParams({ 'LAYERS': 'local:' + curLayerName + '-' + calInfo.time });
                map.addLayer(remoteLayer);
                console.log('切换遥感图层:', curLayerName + '-' + calInfo.time);
            }
        }
        else if (/^NDVI|NDWI|NDBI|CDI$/.test(id)) {
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

    $("#ImageLayer").click();
});


function setSingleLayer(layer) {
    map.getLayers().clear();
    map.addLayer(layer);
}


function toggleLayer(layer) {
    map.getLayers().getArray().includes(layer) ? map.removeLayer(layer) : map.addLayer(layer);
}


// 创建绘制源
const drawSource = new ol.source.Vector();
let draw = null; // 当前的绘制交互
const drawLayer = new ol.layer.Vector({
    source: drawSource,
    zIndex: 100
});
function startSelection() {
    // 清理之的交互
    if (draw) {
        map.removeInteraction(draw);
    }

    // 清除之前的图层
    map.removeLayer(drawLayer);

    // 清空绘制源
    drawSource.clear();

    // 创建新的绘制交互
    draw = new ol.interaction.Draw({
        source: drawSource,
        type: 'Polygon'
    });

    // 添加绘制交互
    map.addInteraction(draw);

    // 事件监听器处理
    draw.once('drawend', function (event) {
        const feature = event.feature; // 获取绘制的特征
        var geometry = feature.getGeometry(); // 获取几何信息

        calInfo.coordinates = geometry.getCoordinates();

        console.log('绘制结束得到的坐标:', calInfo.coordinates);

        // 移除绘制交互并添加图层
        map.removeInteraction(draw);
        map.addLayer(drawLayer);
    });

    // 确认按钮点击事件
    $("#SubmitButton").off('click').on('click', function () {
        // 如果没有选择范围则直接返回
        if (!map.getLayers().getArray().includes(drawLayer)) {
            return;
        }

        calInfo.imageType = curLayerName.split('-')[0];
        calInfo.areaCode = curLayerName.split('-')[1];

        showDialog();
    });

    // 取消按钮点击事件
    $("#ResetButton").off('click').on('click', function () {
        map.removeLayer(drawLayer);

        startSelection(); // 重新开始选择
    });
}


function sendInfo() {

    const coordinates3857 = calInfo.coordinates[0];

    console.log('原始坐标:', coordinates3857);

    let coordinates4326 = [];

    for (let i = 0; i < coordinates3857.length; i++) {
        coordinates4326[i] = ol.proj.toLonLat(coordinates3857[i]);
    }

    console.log('转换至EPSG:4326坐标:', coordinates4326);

    // 通过 AJAX 发送数据到服务器
    $.ajax({
        type: "POST",
        url: "/calculate",
        contentType: "application/json",
        data: JSON.stringify({
            calculateTypes: Array.from(calInfo.calculateTypes),
            imageType: calInfo.imageType,
            areaCode: calInfo.areaCode,
            time: calInfo.time,
            coordinates: coordinates4326
        }),
        dataType: "json",
        beforeSend: function () {
            showLoading();
        },
        success: function (response) {
            console.log('Server response:', response);
            showResult(response);
        },
        error: function (error) {
            console.error('Error:', error);
        },
        complete: function () {
            hideLoading();
        }
    });
}


var resultID = 0;
var resultMap = new Map();
function showResult(response) {
    const imageType = response.imageType;
    const areaCode = response.areaCode;
    const time = response.time;

    for (const key in response.results) {
        const calculateType = key;
        const geoserverLayerName = response.results[key];

        // 生成新的 resultID
        const currentID = resultID++;

        const resultLayer = new ol.layer.Tile({
            source: new ol.source.TileWMS({
                url: 'http://localhost:8080/geoserver/wms',
                params: {
                    'LAYERS': geoserverLayerName,
                    'TILED': true
                },
                serverType: 'geoserver',
                transition: 0
            }),
            zIndex: 10
        });

        // 存储 resultID 和 resultLayer 的映射关系
        resultMap.set(currentID, resultLayer);

        const downloadUrl = `http://localhost:8080/geoserver/wcs?service=WCS&version=2.0.1&request=GetCoverage&coverageId=${geoserverLayerName}&format=image/tiff`
        const downloadButton = $('<a>', {
            href: downloadUrl,
            text: '🔽',
            class: 'download-button',
            target: '_blank',
            download: '' // 这会提示浏览器下载文件而不是直接打开
        });

        const listItem = $('<li>', {
            id: `ResultItem-${currentID}`
        }).append(
            `${calculateType}-${imageType}-${areaCode}-${time} `
        ).append(
            downloadButton
        );

        $('#ResultList').append(listItem);

        // 主动显示结果图层
        $('#ResultItem-' + currentID).click();
    }
}


function getResultLayerByID(id) {
    return resultMap.get(Number(id));
}


function initAvailableDates() {
    // 清空现有选项
    $('#YearSelect').empty();
    $('#MonthSelect').empty();

    // 通过 AJAX 发送数据到服务器
    $.ajax({
        type: "POST",
        url: "/get_available_dates",
        contentType: "application/json",
        data: JSON.stringify({
            imageType: curLayerName.split('-')[0],
            areaCode: curLayerName.split('-')[1]
        }),
        dataType: "json",
        success: function (response) {
            console.log('Server response:', response);
            // 获取年份和月份数据
            var dates = response.dates;

            // 提取并填充年份下拉列表
            var years = [...new Set(dates.map(date => date.year))].sort((a, b) => a - b);
            years.forEach(year => {
                $('#YearSelect').append($('<option>', {
                    value: year,
                    text: year
                }));
            });

            // 根据所选年份更新月份下拉列表
            function updateMonths(selectedYear) {
                $('#MonthSelect').empty(); // 清空现有选项
                // 从 dates 中筛选出对应年份的月份，并去重
                var months = [...new Set(dates
                    .filter(date => date.year === selectedYear)
                    .map(date => date.month))];

                // 按月份升序排序
                months.sort((a, b) => a - b);

                // 填充月份下拉列表
                months.forEach(month => {
                    $('#MonthSelect').append($('<option>', {
                        value: month,
                        text: month
                    }));
                });

                // 默认选择最后一个月份（即最新的月份）
                if (months.length > 0) {
                    $('#MonthSelect').val(months[months.length - 1]);
                }
            }

            // 初始化月份下拉列表
            $('#YearSelect').change(function () {
                var selectedYear = $(this).val();
                updateMonths(selectedYear);
                onSelectionChange();
            });

            $('#MonthSelect').change(function () {
                onSelectionChange();
            });

            // 默认选择第一个年份并更新月份
            if (years.length > 0) {
                $('#YearSelect').val(years[0]).change();
            }
        },
        error: function (error) {
            console.error('Error:', error);
        }
    });
}

// 处理年份和月份选择完成后的操作
function onSelectionChange() {
    var selectedYear = $('#YearSelect').val();
    var selectedMonth = $('#MonthSelect').val();

    if (selectedYear && selectedMonth) {
        // 执行选择完成后的操作
        console.log(`Year: ${selectedYear}, Month: ${selectedMonth}`);
        calInfo.time = `${selectedYear}${selectedMonth}`;
        remoteSource.updateParams({ 'LAYERS': 'local:' + curLayerName + '-' + calInfo.time });
    }
}

function getAvailableImages() {
    // 通过 AJAX 发送数据到服务器
    $.ajax({
        type: "POST",
        url: "/get_available_images",
        contentType: "application/json",
        data: JSON.stringify({}),
        dataType: "json",
        success: function (response) {
            console.log('Server response:', response);

            for (const imageType in response.areaCodes) {
                // console.log(response.areaCodes[imageType])

                for (const areaCode of response.areaCodes[imageType]) {
                    console.log(areaCode);
                    const listItem = $('<li>', {
                        id: `${imageType}-${areaCode}`
                    }).append(
                        `${imageType}-${areaCode}`
                    );
                    if (imageType === 'Landsat8') {
                        $("#RemoteLayerList-Landsat8").append(listItem);
                    }
                    else if (imageType === 'Sentinel2') {
                        $("#RemoteLayerList-Sentinel-2").append(listItem);
                    }
                    else if (imageType === 'MODIS') { 
                        $("#RemoteLayerList-MODIS").append(listItem);
                    }
                }
            }
        },
        error: function (error) {
            console.error('Error:', error);
        }
    });
}


function showDialog() {
    const coordinates3857 = calInfo.coordinates[0];
    let coordinates4326 = [];
    for (let i = 0; i < coordinates3857.length; i++) {
        coordinates4326[i] = ol.proj.toLonLat(coordinates3857[i]);
    }

    // 显示对话框和背景
    $('#DialogOverlay').fadeIn();
    $('#CheckDialog').fadeIn();

    // 填充信息
    $('#CalculateTypesInfo').text(Array.from(calInfo.calculateTypes).join(', '));
    $("#ImageNameInfo").text(`${calInfo.imageType}-${calInfo.areaCode}`);
    $('#DateInfo').text(calInfo.time);
    $('#CoordinatesInfo').html(coordinates4326.map(coord => `(${coord[0].toFixed(4)}, ${coord[1].toFixed(4)})`).join('<br>'));

    // 确认按钮事件
    $('#ConfirmButton').off('click').on('click', function() {
        console.log('用户确认:', coordinates4326, calInfo.calculateTypes);
        closeDialog();

        // 发送相关数据到服务器
        sendInfo();

        map.removeLayer(drawLayer);

        startSelection(); // 重新开始选择
    });

    // 取消按钮事件
    $('#CancelButton').off('click').on('click', function() {
        console.log('用户取消');
        closeDialog();
    });
}


function closeDialog() {
    $('#DialogOverlay').fadeOut();
    $('#CheckDialog').fadeOut();
}


function showLoading() {
    $("#Loading").fadeIn();
}


function hideLoading() {
    $("#Loading").fadeOut();
}