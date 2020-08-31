$('#directions-home').append('<i class="fas fa-home fa-lg px-2 py-1"></i>');

$('#directions-gasstation').append('<i class="fas fa-gas-pump fa-lg px-2 py-1"></i>');

$('#directions-pharmacy').append('<i class="fas fa-prescription fa-lg px-2 py-1"></i>');

$('#directions-hospital').append('<i class="fas fa-ambulance fa-lg px-2 py-1"></i>');

$('#directions-policestation').append('<i class="fas fa-shield-alt fa-lg px-2 py-1"></i>');

if ($(".pamphlet")) {
    setTimeout(function () {
        $(".pamphlet").fadeIn(700);
    }, 200)
};