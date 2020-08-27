
$(async function () {

  const $searchTrailForm = $('#search-trail-form')
  const $searchPlace = $("#place-search-input")
  const $within = $("#radius")

  // m_key is maqpest api key

  if ($('#place-search-input')[0]) {
    placeSearch({
      key: m_key,
      container: document.querySelector('#place-search-input')
    });
  }

  // *****************
  // GENERAL UI AND POPOVERS
  // *****************

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

  $("body").on("click", function () {
    $('#dimmer').removeClass('body-shadow');
  });


  // *****************
  // TRAIL SEARCH FORM UI
  // *****************

  $searchTrailForm.on("submit", async function (event) {
    event.preventDefault();
    $('#loading').append($(`<i class="far fa-compass fa-5x fa-spin"></i>`))

    const results = await SearchTrailList.getTrails($searchPlace.val(), $within.val());
    $('#search-results').children().remove();

    for (let result of results.data) {
      const resultDiv = generateResultHTML(result);
      $('#search-results').append(resultDiv);
    };

    $('#results-number').text(`(Found ${results.data.length} Trails)`);


    $('#loading').children().remove();

    $('#results-container').slideDown(500);

    $([document.documentElement, document.body]).animate({
      scrollTop: $(".spacer").offset().top
    }, 600);

  });



  // *****************
  // VARIOUS FUNCTIONS
  // *****************


  function generateResultHTML(result) {
    let resultMarkup;

    if (result.imgMedium === "") {
      result.imgMedium = "/static/images/no-image.png"
    };

    resultsMarkup = $(`

<a href="#" class="list-group-item list-group-item-action mb-1" data-toggle="modal"
    data-target="#exampleModal${result.id}">
    <div class="d-flex w-100 justify-content-between">
        <h5 class="mb-1">${result.name}</h5>
        <small>${result.difficulty[0]}</small>
    </div>
    <p class="mb-1">${result.summary}</p>
    <small>Rating: ${result.stars} out of 5 (${result.starVotes})</small>
</a>

<div class="modal fade" id="exampleModal${result.id}" tabindex="-1" aria-labelledby="exampleModalLabel"
    aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header text-center py-1">
                <h5 class="modal-title" id="exampleModalLabel">${result.name}</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-7">
                        <img src="${result.imgMedium}" class="rounded img-fluid" alt="...">
                    </div>
                    <div class="col-5">
                        <blockquote class="blockquote font-italic">
                          <p class="mb-0">${result.summary}</p>
                        </blockquote>
                        <hr>
                        <ul class="ml-0">
                          <li>Location: ${result.location}</li>
                          <li>Length: ${result.length} miles</li>
                          <li>Difficulty: ${result.difficulty[0]}</li>
                          <li>
                            <small>
                            <a target="_blank" href="https://www.hikingproject.com/trail/${result.id}/${result.name}">
                              (...more info about this trail)
                            </a>
                            </small>
                          </li>
                        <ul>
                        
                    </div>
                </div>
            </div>
            <div class="modal-footer justify-content-center">
                <p class="lead mr-5">Is this your hike?</p>
                <a href="/trails/${result.id}/secure" class="btn btn-success">Yes</a>
                <button type="button" class="btn btn-danger" data-dismiss="modal">No</button>

            </div>
        </div>
    </div>
</div>
    
`);

    return resultsMarkup
  }

});
