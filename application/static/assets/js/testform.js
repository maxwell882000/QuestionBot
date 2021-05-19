$(function() {
    $('#addOptionBtn').click(addOptionHandler);
    $('input:checkbox').change(checkBoxCheckedHandler);
    $('.option-delete a').click(deleteBtnHandler);
});

function deleteBtnHandler() {
    let idNumber = $(this).attr('data-number');
    $(document.getElementById(idNumber)).remove();
}

function addOptionHandler() {
    let templateString = $('#option-template').html();
    let currentOptionNumber = $(".test-option-item").length;
    templateString = templateString.replace(new RegExp('#optionNumber', 'g'), currentOptionNumber);
    let optionNode = $(templateString);
    optionNode.find('input:checkbox').change(checkBoxCheckedHandler);
    $('#testOptionsList').append(optionNode);
    optionNode.find('input:text').focus();
    optionNode.find('.option-delete a').click(deleteBtnHandler);
    $('html, body').animate({
        scrollTop: optionNode.offset().top
    });
}

function checkBoxCheckedHandler() {
    let checkedCheckbox = $('input:checked');
    for (let i = 0; i < checkedCheckbox.length; i++) {
        if (checkedCheckbox[i] !== this) {
            checkedCheckbox[i].checked = false;
            $(checkedCheckbox[i]).removeAttr('value');
        }
    }
    $(this).attr("value", "True");
    return false;
}