// 添加问卷
$("#save").click(function () {
    var $title = $("#id_title").val('');
    var $classroom_id = Number($("#id_classroom").val(''));

    var $help1 = $("#help-title").html('');
    var $help2 = $("#help-classroom").html('');

    if (!title) {
        $help1.html('问卷标题不能为空');
    }
    else if (!classroom_id) {
        $help2.html('调查班级不能为空');
    }
    else {
        $("#add_naire").modal('hide');

        $.post({
            url: '/add/',
            headers: {"X-CSRFToken": $.cookie('csrftoken')},
            data: JSON.stringify({"title": $title, "classroom_id": classroom_id}),
            contentType: 'application/json',
            success: function (res_dict) {
                if (res_dict['status']) {
                    console.log('成功');
                }
                else {
                    console.log('失败');
                }
            }
        })

    }
});


// 给删除标签绑定事件
$("tbody").on('click', '.delete', function () {
    var $remove_el = $(this).parent().parent();

    $.get({
        url: '/delete/',
        data: {
            'naire_id': Number($remove_el.attr('id').split('_')[1])
        },
        success: function (res_dict) {
            if (res_dict['status']) {
                $remove_el.remove();
            }
        }
    })
});

