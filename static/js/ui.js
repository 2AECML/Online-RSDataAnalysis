
let curVectorLayerNum = 0;
let curRasterLayerNum = 0;

$(document).ready(function () {
    // 默认展开图层列表
    $('#LayerList').show();

    $('#LayerHeader').click(function() {
        $('#LayerList').slideToggle();
    });

    $('.nav-subheader').click(function (event) {
        if ($(event.target).is('.nav-sublist li') || $(event.target).is('.band-header')) return;
        $(this).toggleClass('active');
        $(this).find('.nav-sublist').slideToggle();
    });

    $('.nav-sublist').on('click', '.band-header', function (event) {
        if ($(event.target).is('.band-list li')) return;
        $(this).toggleClass('active');
        $(this).find('li').slideToggle();
    });

    $('.nav-sublist').on('click', 'li', function (event) {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
            if ($(event.target).is('#VectorLayerHeader *') || $(event.target).is("#RasterLayerHeader *")) {
                if ($(event.target).is('#VectorLayerHeader *') && --curVectorLayerNum > 0) {
                    return;
                }
                else if ($(event.target).is('#RasterLayerHeader *') && --curRasterLayerNum > 0) {
                    return;
                }
            }
            $(this).parents('.nav-subheader').removeClass('list-item-active');
            $(this).parents('.band-header').removeClass('list-item-active');
        }
        else {
            if (!$(event.target).is('#VectorLayerHeader *') && !$(event.target).is("#RasterLayerHeader *")) {
                $(this).parent().children().removeClass('active');
            }
            else {
                if ($(event.target).is('#VectorLayerHeader *')) ++curVectorLayerNum;
                else if ($(event.target).is('#RasterLayerHeader *')) ++curRasterLayerNum;
            }
            $(this).addClass('active');
            $(this).parents('.nav-subheader').addClass('list-item-active');
            $(this).parents('.band-header').addClass('list-item-active');
        }
    });

    $('#FunctionHeader').click(function() {
        $('#FunctionList').slideToggle();
    });

    $('#FunctionList li').click(function () {
        $(this).toggleClass('active');
        $('.draw-control-button').show();
    });

    $('#ResultHeader').click(function() {
        $('#ResultList').slideToggle();
    });

    $('#ResultList').on('click', 'li', function () {
        $('#ResultList').slideDown();
        $(this).toggleClass('active');
    });

    $('#ToggleButton').click(function () {
        $('.date-picker').toggle();;
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
