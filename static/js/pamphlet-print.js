let saveData = (function () {
    let a = document.createElement("a");
    document.body.appendChild(a);
    a.style = "display: none";
    return function (data, fileName) {
        blob = new Blob([data], { type: "octet/stream" }),
            url = window.URL.createObjectURL(blob);
        a.href = url;
        a.download = fileName;
        a.click();
        window.URL.revokeObjectURL(url);
    };
}());


function processPamphletData() {
    const homeDirections = $('#list-home-directions').children('ol').children().children('span');
    const gasDirections = $('#list-gasstation-directions').children('ol').children().children('span');
    const pharmacyDirections = $('#list-pharmacy-directions').children('ol').children().children('span');
    const hospitalDirections = $('#list-hospital-directions').children('ol').children().children('span');
    const policeDirections = $('#list-policestation-directions').children('ol').children().children('span');



    const directionSet = {
        'HOME': [
            homeDirections,
            $('.home-name'),
            $('.trail-name')
        ],
        'GAS STATION': [
            gasDirections,
            $('.gasstation-name'),
            $('.gasstation-address1'),
            $('.gasstation-address2')
        ],
        'PHARMACY': [
            pharmacyDirections,
            $('.pharmacy-name'),
            $('.pharmacy-address1'),
            $('.pharmacy-address2')
        ],
        'HOSPITAL': [
            hospitalDirections,
            $('.hospital-name'),
            $('.hospital-address1'),
            $('.hospital-address2')
        ],
        'POLICE STATION': [
            policeDirections,
            $('.policestation-name'),
            $('.policestation-address1'),
            $('.policestation-address2')
        ]
    };

    for (let destination in directionSet) {
        for (let i = 1; i < directionSet[destination].length; i++) {
            let rawText = directionSet[destination][i].text()
            directionSet[destination][i] = rawText.trim().replace(/\s+/g, ' ');
        }
    };


    let data = $('.current-user-name').text().trim() + "'s " + "AFTER-THE-HIKE PAMPHLET"
        + "\n" + "FROM "
        + directionSet['HOME'][2].toUpperCase();

    for (let destination in directionSet) {

        if (destination === 'HOME') {
            data = data + "\n" + "\n" +
                "*************************"
                + "\n" + destination
                + "\n" + "*************************"
                + "\n";

            data = data + directionSet[destination][1] + "\n" + "\n";
            data = data + "DIRECTIONS: " + "\n";

            for (i = 0; i < directionSet[destination][0].length; i++) {
                data = data + `${i + 1}. ` + directionSet[destination][0][i].innerText.trim() + "\n"
            }

        };

        if (destination !== 'HOME') {
            data = data + "\n" + "\n" +
                "*************************"
                + "\n" + "NEAREST " + destination
                + "\n" + "*************************"
                + "\n";

            data = data + directionSet[destination][1] + "\n"
            data = data + directionSet[destination][2] + " " + directionSet[destination][3] + "\n" + "\n";
            data = data + "DIRECTIONS: " + "\n";

            for (i = 0; i < directionSet[destination][0].length; i++) {
                data = data + `${i + 1}. ` + directionSet[destination][0][i].innerText.trim() + "\n"
            }
        }
    }
    return data;
}

$('#text-file-pamphlet').on("click", function () {
    let pamphlet = processPamphletData();
    let fileName = "your_pamphlet.txt";
    saveData(pamphlet, fileName)
})

$('#email-pamphlet').on("submit", async function (evt) {
    evt.preventDefault();
    let pamphlet = processPamphletData();

    $('#email-loading').append(`<i class="fas fa-spinner fa-spin dark-icon"></i>`)
    const response = await Pamphlet.emailPamphlet(pamphlet,
        this.dataset.user_id,
        this.dataset.pamphlet_id,
        $('#email-input').val())
    $('#email-loading').children().remove()

    if (response.data === "Sent Email!") {
        $('#email-loading').append(`
        <div class="alert alert-success temp" role="alert">
            ${response.data}
        </div>`);
    } else {
        $('#email-loading').append(`
        <div class="alert alert-warning temp" role="alert">
            ${response.data}
        </div>`);
    }

    setTimeout(function () {
        $('.temp').fadeOut();

        if (response.data === "Sent Email!") {
            $("#emailModal").modal('hide')
        };

    }, 1500)
})