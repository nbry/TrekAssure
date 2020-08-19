$('.hidden').hide()

$('.testing1').on('click', function () {
    if ($(this).children('.testing').hasClass('hidden')) {
        $(this).children('.testing').slideDown().removeClass('hidden')
        $(this).addClass('active');
    } else {
        $(this).children('.testing').slideUp().addClass('hidden')
        $(this).removeClass('active');
    }
})
