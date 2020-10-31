$(function () {
    if (!$('#id_race input[value="O"]')[0].checked) {
        $('#id_race_other').parent().hide();
    }
    $('#id_race input[value="O"]').click(function () {
        if ($('#id_race input[value="O"]')[0].checked) {
            $('#id_race_other').parent().show();
        }
        else {
            $('#id_race_other').parent().hide();
        }
    });

    if ($('#id_gender').val() !== "X") {
        $('#id_gender_other').parent().hide();
    }
    $('#id_gender').on('change', function () {
        let selection = $('#id_gender').val();
        if (selection === "X") {
            $('#id_gender_other').parent().show();
        }
        else {
            $('#id_gender_other').parent().hide();
        }
    });

    if (!$('#id_where_did_you_hear input[value="O"]')[0].checked) {
        $('#id_where_did_you_hear_other').parent().hide();
    }
    $('#id_where_did_you_hear input[value="O"]').click(function () {
        if ($('#id_where_did_you_hear input[value="O"]')[0].checked) {
            $('#id_where_did_you_hear_other').parent().show();
        }
        else {
            $('#id_where_did_you_hear_other').parent().hide();
        }
    });


    if (!$('#id_shipping_address').val()) {
        $('#id_address1').parent().hide();
        $('#id_address2').parent().hide();
        $('#id_city').parent().hide();
        $('#id_state').parent().hide();
        $('#id_zip_code').parent().hide();
    }
    $('#id_shipping_address').on('change', function () {
        console.log($('#id_shipping_address').val());
        if ($('#id_shipping_address').val()) {
            $('#id_address1').parent().show();
            $('#id_address2').parent().show();
            $('#id_city').parent().show();
            $('#id_state').parent().show();
            $('#id_zip_code').parent().show();
        }
        else {
            $('#id_address1').parent().hide();
            $('#id_address2').parent().hide();
            $('#id_city').parent().hide();
            $('#id_state').parent().hide();
            $('#id_zip_code').parent().hide();
        }
    });

    if ($('#id_school option:selected').text() !== "Other") {
        $('#id_school_other').parent().hide();
    }
    $('#id_school').on('change', function () {
        let selection = $('#id_school option:selected').text();
        if (selection === "Other") {
            $('#id_school_other').parent().show();
        }
        else {
            $('#id_school_other').parent().hide();
        }
    });
})
