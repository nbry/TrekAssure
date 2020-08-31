
$(async function () {

  const $searchTrailForm = $('#search-trail-form')
  const $searchPlace = $("#place-search-input")
  const $radius = $("#radius")

  // m_key is mapquest API key
  


  // *****************
  // GENERAL UI AND POPOVERS
  // *****************

  // POPOVER
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

  // Flash messages fade out automatically
  if ($("span.alert")) {
    setTimeout(function () {
      $("span.alert").fadeOut(800);
    }, 2000)
  };

  // Secure form spinner
  if ($("#secure-form-btn")) {
    $("#secure-form").on("submit", function () {
      $("#secure-loading").children().remove();
      $("#secure-loading").append($(`<i class="fas fa-compass fa-3x fa-spin"></i>`));
    })
  };

  applyOpenCloseSecureForm();
  applyMapquestSearchSDK()


  // *****************
  // TRAIL SEARCH FORM UI
  // *****************

  $searchTrailForm.on("submit", async function (event) {
    event.preventDefault();
    $('#loading').append($(`<i class="far fa-compass fa-5x fa-spin mt-3 light-icon"></i>`))
    $('#results-container').fadeOut();

    // Ensure Secure Form Modal is moved elsewhere and hidden
    $('#secure-form').appendTo($("#outside-target"));

    // TREKASSURE API call to get results and append:
    const results = await SearchTrailList.getTrails($searchPlace.val(), $radius.val());

    $('#search-results').children().remove();

    if (results.data.length === 0) {
      $('#search-results').append($zeroResults);
    }
    else {
      for (let result of results.data) {
        const resultDiv = generateResultHTML(result);
        $('#search-results').append(resultDiv);
      };

      $('#results-number').text(`(Found ${results.data.length} Trails)`);
    }

    applyOpenCloseSecureForm();
    applyMapquestSearchSDK();

    $('#loading').children().remove();
    $('#results-container').fadeIn(800);
    $([document.documentElement, document.body]).animate({
      scrollTop: $(".spacer").offset().top
    }, 800);

    // TREKASSURE API call to store search result to database
    const search = await SearchTrailList.storeTrailSearch(results.data, $searchPlace.val(), $radius.val());

  });



  // *****************
  // VARIOUS FUNCTIONS
  // *****************

  function applyOpenCloseSecureForm() {
    if ($('.open-secure')) {
      $('.open-secure').on("click", function (e) {
        $('.trail-modal-info').hide();
        $('#secure-form').appendTo($(`#info-modal-target-${e.currentTarget.id}`))
        $('#secure-form').addClass('d-flex').fadeIn();
        $('#secure-form-target').attr('action', `/trails/${e.currentTarget.id}/secure`);
      });

      $('.close-secure').on("click", function () {
        $('.trail-modal-info').fadeIn();
        $('#secure-form').hide().removeClass('d-flex');
      });

      $('.modal').on('hide.bs.modal', function (e) {
        setTimeout(function () {
          $('#secure-form').hide().removeClass('d-flex');
          $('.trail-modal-info').fadeIn();
        }, 200);
      });
    }
  };

  function applyMapquestSearchSDK() {
    if (!m_key) {
      return
    };

    if ($('#place-search-input')[0]) {
      placeSearch({
        key: m_key,
        container: document.querySelector('#place-search-input')
      });
    };

    if ($('#home_address')[0]) {
      placeSearch({
        key: m_key,
        container: document.querySelector('#home_address')
      });
    }
  };




  // *****************
  // GENERATE TRAIL RESULT HTML
  // *****************

  function generateResultHTML(result) {
    let resultsMarkup;

    if (result.imgMedium === "") {
      result.imgMedium = "/static/images/no-image.png"
    };

    resultsMarkup = $(`

<a href="#" class="list-group-item list-group-item-action mb-1" data-toggle="modal"
    data-target="#modal-${result.id}">
    <div class="d-flex w-100 justify-content-between">
        <h5 class="mb-1">${result.name}</h5>
        <small>${result.difficulty[0]}</small>
    </div>
    <p class="mb-1">${result.summary}</p>
    <small>Rating: ${result.stars} out of 5 (${result.starVotes}})</small>
</a>

<div class="modal fade" id="modal-${result.id}" tabindex="-1" aria-labelledby="ModalLabel-${result.id}"
    aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header text-center py-1">
                <h5 class="modal-title" id="ModalLabel-${result.id}">${result.name}</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div id="info-modal-target-${result.id}" data-target-id="${result.id}" class=" modal-body">
                <div class="trail-modal-info row">
                    <div class="col-7">
                        <img src="${result.imgMedium}" class="rounded img-fluid" alt="...">
                    </div>

                    <div class="col-5">
                        <blockquote class="blockquote font-italic">
                            <p class="mb-0">${result.summary}</p>
                        </blockquote>
                        <hr>
                        <ul class="ml-0 p-1">
                            <li>${result.location}</li>
                            <li>${result.length} miles</li>
                            <li>Difficulty: ${result.difficulty[0]}</li>
                            <li>
                                <small>
                                    <a target="_blank"
                                        href="https://www.hikingproject.com/trail/${result.id}/${result.name}}">
                                        (...more info about this trail)
                                    </a>
                                </small>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="modal-footer justify-content-center trail-modal-info">
                <p class="lead mr-3">Is this your hike?</p>
                <a id="${result.id}" type="button" class="open-secure btn btn-lg btn-success mr-3">Yes</a>
                <button type="button" class="btn btn-lg btn-danger" data-dismiss="modal">No</button>
            </div>
        </div>
    </div>
</div>`);

    return resultsMarkup
  };

  const $zeroResults = $(`<p class="lead text-center">No trails found within those search parameters. 
    Try increasing the search radius or choosing a new place altogether. Zip Codes, Park Names, and Cities work well!</p >`);

});
