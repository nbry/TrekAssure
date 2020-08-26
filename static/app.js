



// placeSearch({
//   key: m_key,
//   container: document.querySelector('#place-search-input')
// });


$(function () {
  $('[data-toggle="popover"]').popover()
});

$(function () {
  $('.example-popover').popover({
    container: 'body'
  })
});


$('.popover-dismiss').popover({
  trigger: 'focus'
});


$('#search-help').on("click", function () {
  $('#dimmer').addClass('body-shadow');
});


$("#dimmer").on("click", function () {
  $('#dimmer').removeClass('body-shadow');
});