// 删除问卷里的问题
function del_question(qid) {
    if (!qid) {
        // 如果是JS添加的问题框，qid为0，直接删除
        $("[qid=0]").remove();
    }
    else {
        // 提交ajax请求
        $.ajax({
            url: '/del_question/' + qid,
            success: function (data) {
                var res_dict = JSON.parse(data);
                if (res_dict['status']) {
                    $("[qid=" + qid + "]").remove();
                }
                else {
                    alert('问题删除失败');
                }
            }
        });

    }
}


// 向问卷中添加问题
$("#addQue").click(function () {
    console.log('添加问题');
    var $new_item = $(".questionItem").first().clone().attr('qid', 0).appendTo($("form ol"));
    $("input[name=title]").last().val('');// 清空input框
    var $new_options = $("select[name=type]").last().children();
    $new_options.attr('selected', false);
    $new_options.first().attr('selected', true);//

});
