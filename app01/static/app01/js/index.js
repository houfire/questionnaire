// 点击添加按钮，清空模态框里的内容
$("#add").click(function () {
    $("#id_title").val('');
    $("option:selected").attr('selected', false);
    $("option").first().attr('selected', true);

});

// 点击模态框的“保存”，添加问卷
$("#save").click(function () {
    var $title = $("#id_title");
    var $classroom = $("option:selected");

    var $help1 = $("#help-title").html('');
    var $help2 = $("#help-classroom").html('');

    if (!$title.val()) {
        $help1.html('问卷标题不能为空');
    }
    else if (!$classroom.val()) {
        $help2.html('调查班级不能为空');
    }
    else {
        $("#add_naire").modal('hide');

        $.post({
            url: '/add/',
            headers: {"X-CSRFToken": $.cookie('csrftoken')},
            data: JSON.stringify({"title": $title.val(), "classroom_id": Number($classroom.val())}),
            contentType: 'application/json',
            success: function (res_dict) {
                if (res_dict['status']) {
                    var naire_id = res_dict['naire_id'];
                    var students_cnt = res_dict['students_cnt'];

                    var s = '<tr id="naire_' + naire_id + '">\n' +
                        '        <td><a href="###">' + $title.val() + '</a></td>\n' +
                        '        <td>' + $classroom.html() + '</td>\n' +
                        '        <td>0/' + students_cnt + '</td>\n' +
                        '        <td><a href="/edit/' + naire_id + '/">编辑问卷</a></td>\n' +
                        '        <td> /show/' + $classroom.val() + '/' + naire_id + ' </td>\n' +
                        '        <td><a href="###">查看评分</a></td>\n' +
                        '        <td><a href="javascript:void (0)" class="delete">删除</a></td>\n' +
                        '    </tr>';
                    $("tbody").append(s);

                }
                else {
                    var error_msg = res_dict['error_msg'];
                    //UNIQUE constraint failed: ...
                    if (new RegExp("UNIQUE constraint failed").test(error_msg)) {
                        alert('该问卷已存在，请勿重复添加！')
                    }
                }
            }
        });

    }
});


// 给删除标签绑定事件
$("tbody").on('click', '.delete', function () {
    if (confirm('确认删除？')) {
        var $remove_el = $(this).parent().parent();
        $.get({
            url: '/delete/',
            data: {
                'naire_id': $remove_el.attr('id').split('_')[1]
            },
            success: function (res_dict) {
                if (res_dict['status']) {
                    $remove_el.remove();
                }
                else {
                    alert(res_dict['error_msg']);
                }
            }
        })
    }

});

