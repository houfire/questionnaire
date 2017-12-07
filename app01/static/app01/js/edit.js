// 每次打开网页，生成一个空的、隐藏的questionItem，放在<ol>标签的开头，做克隆的模板
$(function () {
    $(".questionItem:first").clone().attr({"qid": 0, "id": 'modelItem'}).addClass('hidden').prependTo($("form ol"));

    // 清空input框
    $("input[name=title]:first").val('');
    // 重置option标签的selected属性
    var $new_options = $("select[name=type]:first").children();
    $new_options.attr('selected', false);
    $new_options.first().attr('selected', true);

    var $model_ul = $(".questionItem ul:first");
    if ($model_ul.children().length) {
        // 如果克隆的model_questionItem是单选类型，清空选项
        $model_ul.html('');
    }
});

// 用于克隆questionItem标签的函数
function add_que() {
    $("#modelItem").clone().attr("id", null).removeClass('hidden').appendTo($("form ol"));
}

// 点击“添加”按钮，向问卷中添加问题#################
$("#addQue").click(add_que);


// 删除问卷里的问题##############################
$("form").on('click', '.removeQue', function () {
    var itemNum = $(".questionItem").length;// 删除前统计当前questionItem标签的数量
    console.log(itemNum);
    if (itemNum === 2) {
        // 当itemNum=2的时候，说明已有的问题都已经或者即将被删除，此时应该克隆一个新的标签并显示，itemNum会一直等于2,
        add_que();
    }

    var $questionItem = $(this).parent().parent().parent();
    var qid = $questionItem.attr('qid');

    if (qid === '0') {
        // 如果是JS添加的问题框，qid为0，直接删除
        $questionItem.remove();
    }
    else {
        // 如果是数据库中存在的问题，提交ajax请求删除
        $.ajax({
            url: '/del_question/' + qid,
            success: function (data) {
                var res_dict = JSON.parse(data);
                if (res_dict['status']) {
                    $questionItem.remove();
                }
                else {
                    alert('问题删除失败');
                }
            }
        });
    }
});


// 给select框委派事件############################
$("form").on('change', 'select', function () {
    if ($(this).children(':selected').val() === '2') {
        // 如果用户选择的是单选类型，显示“添加选项”按钮
        $(this).parent().next().removeClass('hidden');
        var s = '<div class="form-group">\n' +
            '<label class="control-label col-md-1">● 内容</label>\n' +
            '<div class="col-md-2">\n' +
            '    <input type="text" class="form-control">\n' +
            '</div>\n' +
            '<label class="control-label col-md-1">分值</label>\n' +
            '<div class="col-md-2">\n' +
            '    <input type="text" class="form-control">\n' +
            '</div>\n' +
            '<div class="removeOpt"><span class="glyphicon glyphicon-remove"></span></div>\n' +
            '</div>';
        $(this).parent().parent().next().append(s);
    }
    else {
        $(this).parent().next().addClass('hidden');
        $(this).parent().parent().next().html('');
    }
});


// 点击“添加选项标签”，添加一个选项################
$("form").on('click', '.addOpt', function () {
    var s = '<div class="form-group">\n' +
        '<label class="control-label col-md-1">● 内容</label>\n' +
        '<div class="col-md-2">\n' +
        '    <input type="text" name="content" class="form-control" maxlength="16">\n' +
        '</div>\n' +
        '<label class="control-label col-md-1">分值</label>\n' +
        '<div class="col-md-2">\n' +
        '    <input type="text" name="value" class="form-control" maxlength="16">\n' +
        '</div>\n' +
        '<div class="removeOpt"><span class="glyphicon glyphicon-remove"></span></div>\n' +
        '</div>';
    $(this).parent().parent().next().append(s);
});

// 删除选项#####################################
$("form").on('click', '.removeOpt', function () {
    $(this).parent().remove();
});

// ============================================================================================
$("#save").click(function () {
    var data_list = [];
    $(".questionItem:gt(0)").each(function () {
        var temp_dict = {
            "qid": $(this).attr('qid'),
            "title": $(this).find('input[name=title]').val(),
            "type": $(this).find('select[name=type]').val(),
            "options": []
        };
        if (temp_dict['type'] === '2') {
            $(this).find('ul>.form-group').each(function () {
                var oid = $(this).attr('oid');
                var content = $(this).find('input[name=content]').val();
                var value = $(this).find('input[name=value]').val();
                temp_dict['options'].push({"oid": oid, "content": content, "value": value})
            })
        }
        data_list.push(temp_dict);
    });
    console.log(data_list);
    $.post({
        url: location.pathname,
        headers: {"X-CSRFToken": $.cookie('csrftoken')},
        data: JSON.stringify(data_list),
        contentType: 'application/json',
        success: function (data) {
            console.log('OK');
        }
    })
});