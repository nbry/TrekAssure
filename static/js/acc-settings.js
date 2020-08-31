$('.form-changer').on("click", function (evt) {
    const showElement = evt.currentTarget.dataset['toggleShow'];

    $('.form-update').hide();
    $('.form-back').hide();
    $('.field-target').hide();
    $('.form-changer').fadeIn();
    $('.field-name-header').fadeIn();
    $(`#${showElement}-header`).hide();
    $(evt.currentTarget).hide();

    $(`#form-back-${showElement}`).fadeIn();
    $("#settings-form").appendTo($(`#${showElement}-update`)).fadeIn();
    $(`#${showElement}-target`).fadeIn();
    $("#password-target").fadeIn();
    $(`#${showElement}-update`).fadeIn();

    if (evt.currentTarget === $("#form-changer-new_password")[0]) {
        $('#new-password-header').hide();
    };

})

$('.form-back').on("click", function (evt) {
    const showElement = evt.currentTarget.dataset['toggleShow'];
    $('.form-back').hide();
    $('.form-update').hide();
    $('.field-name-header').fadeIn();
    $('.form-changer').fadeIn();
    $("#settings-form").appendTo($(`#${showElement}-update`)).hide();
    $(`#${showElement}-target`).hide();
})