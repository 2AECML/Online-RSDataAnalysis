$(document).ready(function() {
    // 默认展开图层列表
    $('#LayerList').show();

    $('#LayerHeader').click(function() {
        $('#LayerList').slideToggle();
    });

    $('#VectorLayerHeader').click(function () {
        $(this).toggleClass('active');
        $('#VectorLayerList').slideToggle();
    });

    $('#VectorLayerList li').click(function () {
        if ($(this).hasClass('active')) { 
            $(this).removeClass('active');
            $("#VectorLayerHeader").removeClass('list-item-active');
        }
        else {
            $(this).addClass('active');
            $("#VectorLayerHeader").addClass('list-item-active');
        }
    });

    $('#RasterLayerHeader').click(function () {
        $(this).toggleClass('active');
        $('#RasterLayerList').slideToggle();
    });

    $('#RasterLayerList li').click(function () {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            $("#RasterLayerHeader").removeClass('list-item-active');
        }
        else {
            $(this).addClass('active');
            $("#RasterLayerHeader").addClass('list-item-active');
        }
    });

    $('#RemoteLayerHeader-Landsat8').click(function () {
        $(this).toggleClass('active');
        $('#RemoteLayerList-Landsat8').slideToggle();
    });

    $('#RemoteLayerList-Landsat8 li').click(function () {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            $("#RemoteLayerHeader-Landsat8").removeClass('list-item-active');
        }
        else {
            $(this).parent().children().removeClass('active');
            $(this).addClass('active'); 
            $("#RemoteLayerHeader-Landsat8").addClass('list-item-active');
        }
    });

    $('#RemoteLayerHeader-Sentinel-2').click(function () {
        $(this).toggleClass('active');
        $('#RemoteLayerList-Sentinel-2').slideToggle();
    });

    $('#RemoteLayerList-Sentinel-2 li').click(function () {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            $("#RemoteLayerHeader-Sentinel-2").removeClass('list-item-active');
        }
        else {
            $(this).parent().children().removeClass('active');
            $(this).addClass('active'); 
            $("#RemoteLayerHeader-Sentinel-2").addClass('list-item-active');
        }
    });

    $('#RemoteLayerHeader-MODIS').click(function () {
        $(this).toggleClass('active');
        $('#RemoteLayerList-MODIS').slideToggle();
    });

    $('#RemoteLayerList-MODIS li').click(function () {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            $("#RemoteLayerHeader-MODIS").removeClass('list-item-active');
        }
        else {
            $(this).parent().children().removeClass('active');
            $(this).addClass('active'); 
            $("#RemoteLayerHeader-MODIS").addClass('list-item-active');
        }
    });

    $('#FunctionHeader').click(function() {
        $('#FunctionList').slideToggle();
    });

    $('#FunctionList li').click(function () {
        $(this).toggleClass('active');
        $('.draw-control-button').css('display', 'block');
    });

    $('#ResultHeader').click(function() {
        $('#ResultList').slideToggle();
    });

    $('#ResultList').on('click', 'li', function () {
        $('#ResultList').slideDown();
        $(this).toggleClass('active');
    });

    // 改变navigation栏的宽度
    var isResizing = false;
    var lastX;
    $('.resize-handle').on('mousedown', function (e) {
        isResizing = true;
        lastX = e.clientX;
        $(document).on('mousemove', handleMouseMove);
        $(document).on('mouseup', function () {
            isResizing = false;
            $(document).off('mousemove', handleMouseMove);
        });
    });

    function handleMouseMove(e) {
        if (isResizing) {
            var newWidth = $('.navigation').width() + (e.clientX - lastX);
            // Ensure the width is within reasonable bounds (e.g., min 150px)
            newWidth = Math.max(newWidth, 150); 
            $('.navigation').width(newWidth);
            lastX = e.clientX;
        }
    }
});
