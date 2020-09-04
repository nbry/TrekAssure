$(async function () {

  const $searchTrailForm = $('#search-trail-form')
  const $searchPlace = $("#place-search-input")
  const $radius = $("#radius")

  // m_key is mapquest API key
  const m_key_request = await axios.get("/key")
  const m_key = m_key_request.data

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

  //Item Loading Animations (class must be hidden)
  if ($(".animate-loading")[0]) {
    setTimeout(function () {
      $(".animate-loading").fadeIn(650);
    }, 150);

    setTimeout(function () {
      $(".animate-loading").removeClass("hidden");
    }, 1000)
  };

  // Secure form spinner
  if ($("#secure-form-btn")[0]) {
    $("#secure-form").on("submit", function () {
      $("#secure-loading").children().remove();
      $("#secure-loading").append($(`<i class="fas fa-compass fa-3x fa-spin"></i>`));
    })
  };

  // Quote Box animator
  if ($("#quotes-box")[0]) {
    $(".qnow").show();

    setInterval(function () {
      const currentQuote = parseInt($(".qnow")[0].dataset.quote)

      if (currentQuote < $('.quote').length) {
        $(".qnow").fadeOut(500).removeClass("qnow");
        $(`.q${currentQuote + 1}`).delay(500).fadeIn(300).addClass("qnow")
      } else {
        $(".qnow").fadeOut(500).removeClass("qnow");
        $(`.q1`).delay(500).fadeIn(300).addClass("qnow")
      }
    }, 10000)
  }

  applyOpenCloseSecureForm();
  applyMapquestSearchSDK(m_key);

  // *****************
  // TRAIL SEARCH FORM UI
  // *****************

  $searchTrailForm.on("submit", async function (event) {
    event.preventDefault();
    $('#loading').append($(`<i class="far fa-compass fa-4x fa-spin mt-3 light-icon"></i>`))
    $('#results-container').fadeOut();

    // Ensure Secure Form Modal is moved elsewhere and hidden
    $('#secure-form').appendTo($("#outside-target"));

    // TREKASSURE API call to get results and append:
    const results = await SearchTrailList.getTrails($searchPlace.val(), $radius.val());

    // Populate Data Table
    const table = $('#trails-table').DataTable();
    table.rows().remove().draw();

    for (let result of results.data) {
      const element = generateResultHTML(result);
      table.row.add(element.trailRow).draw();
      $('#trail-modals').append(element.trailModal);
    };

    if (results.data.length === 0) {
      $('#results-number').append($zeroResults);
      $('.table-container').hide();
    } else {
      $('#results-number').text(`(Found ${results.data.length} Trails)`);
      $('.table-container').show();
    };

    applyOpenCloseSecureForm();

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
    if ($('.open-secure')[0]) {
      $('.open-secure').on("click", function (e) {
        $('.trail-modal-info').hide();
        $('#secure-form').appendTo($(`#info-modal-target-${e.currentTarget.id}`))
        $('#secure-form').fadeIn();
        $('#secure-form-target').attr('action', `/trails/${e.currentTarget.id}/secure`);
      });

      $('.close-secure').on("click", function () {
        $('.trail-modal-info').fadeIn();
        $('#secure-form').hide();
      });

      $('.modal').on('hide.bs.modal', function (e) {
        setTimeout(function () {
          $('#secure-form').hide().removeClass('d-flex');
          $('.trail-modal-info').fadeIn();
        }, 200);
      });
    }
  };

  function applyMapquestSearchSDK(m_key) {
    if ($('.m-search')[0]) {
      for (let search of $('.m-search')) {
        placeSearch({
          key: m_key,
          container: search
        });
      }
    };
  };


  // *****************
  // GENERATE TRAIL RESULT HTML
  // *****************

  function generateResultHTML(result) {
    let trailRow = {};
    let trailModal

    if (result.imgMedium === "") {
      result.imgMedium = "/static/images/no-image.webp"
    };

    trailRow =
    {
      0: `<a href="#" data-toggle="modal" data-target="#modal-${result.id}">
                    ${result.name}</a>`,
      1: `${result.short_sum}`,
      2: `${result.stars} out of 5(${result.starVotes})`,
      3: `${result.difficulty[0]}`
    };

    if (result.name.length > 20) {
      trailRow[0] = `<a href="#" data-toggle="modal" data-target="#modal-${result.id}">
      ${result.short_name}</a>`
    };

    trailModal = $(`

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
                <div id="info-modal-target-${result.id}" data-target-id="${result.id}"
                  class=" modal-body container">
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
                                  href="https://www.hikingproject.com/trail/${result.id}/${result.name}">
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
              </div>
    `)

    return { trailModal, trailRow }
  };

  const $zeroResults = $(`<p class="lead text-center">No trails found within those search parameters.
    Try increasing the search radius or choosing a new place altogether. Zip Codes, Park Names, and Cities work well!</p >`);

});
