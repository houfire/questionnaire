var num = 0;

$("#add").click(function () {
    num += 1;
    var $main = $(".main");
    var $questionItem = $("<div>").appendTo($main);
    $("<div>", {"class": 'pull-left', html: '问题' + num}).appendTo($questionItem);
    var $div = $("<div>", {"class": 'form-group'}.appendTo($questionItem);
    $("<label>", {
        "for": 'question_' + num,
        "class": 'col-md-1',
        html: '问题：'
    }).appendTo($div);
    $("<input>", {"type": 'text', "class": 'form-control col-md-9'}).appendTo($div);

});


$("#save").click(function () {
    console.log('保存问卷')
});