

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


function showResult(response) {
    const imageType = response.imageType;
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

        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0'); // 获取小时并补零
        const minutes = String(now.getMinutes()).padStart(2, '0'); // 获取分钟并补零
        const seconds = String(now.getSeconds()).padStart(2, '0'); // 获取秒并补零

        const curTime = `${hours}:${minutes}:${seconds}`; // 结果格式为 HH-MM-SS

        const fileName = `${calculateType}-${imageType}-${time}-${curTime}.tif`

        const downloadUrl = `http://localhost:8080/geoserver/wcs?service=WCS&version=2.0.1&request=GetCoverage&coverageId=${geoserverLayerName}&format=image/tiff&filename=${fileName}`
        const downloadButton = $('<a>', {
            href: downloadUrl,
            text: '🔽',
            class: 'download-button',
            target: '_self',
        });

        const listItem = $('<li>', {
            id: `ResultItem-${currentID}`
        }).append(
            `${calculateType}-${imageType}-${time}-${curTime}`
        ).append(
            downloadButton
        );

        $('#ResultList').append(listItem);

        // 主动显示结果图层
        $('#ResultItem-' + currentID).click();
    }
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
    $("#ImageNameInfo").text(`${calInfo.imageType}`);
    $('#DateInfo').text(calInfo.time);
    $('#CoordinatesInfo').html(coordinates4326.map(coord => `(${coord[0].toFixed(4)}, ${coord[1].toFixed(4)})`).join('<br>'));

    // 确认按钮事件
    $('#ConfirmButton').off('click').on('click', function () {
        console.log('用户确认:', coordinates4326, calInfo.calculateTypes);

        if (!checkCalInfo()) return;

        closeDialog();

        // 发送相关数据到服务器
        sendInfo();

        map.removeLayer(drawLayer);

        startSelection(); // 重新开始选择
    });

    // 取消按钮事件
    $('#CancelButton').off('click').on('click', function () {
        console.log('用户取消');
        closeDialog();
    });
}


function checkCalInfo() {
    return calInfo.calculateTypes.size > 0
        && calInfo.imageType != ''
        && calInfo.time != ''
        && calInfo.coordinates.length > 0
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

