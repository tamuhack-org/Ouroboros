$(function() {
    if (!$('#id_race input[value="O"]')[0].checked) {
        $('#id_race_other').parent().hide();
    }
    $('#id_race input[value="O"]').click(function() {
        if ($('#id_race input[value="O"]')[0].checked){
            $('#id_race_other').parent().show();
        }
        else{
            $('#id_race_other').parent().hide();
        }
    });

    if ($('#id_gender').val() !== "X"){
        $('#id_gender_other').parent().hide();
    }
    $('#id_gender').on('change', function(){
         let selection = $('#id_gender').val();
         if (selection === "X"){
            $('#id_gender_other').parent().show();
         }
         else{
             $('#id_gender_other').parent().hide();
         }
    });

    if (!$('#id_hear_about input[value="O"]')[0].checked) {
        $('#id_hear_about_other').parent().hide();
    }
    $('#id_hear_about input[value="O"]').click(function() {
        if ($('#id_hear_about input[value="O"]')[0].checked){
            $('#id_hear_about_other').parent().show();
        }
        else{
            $('#id_hear_about_other').parent().hide();
        }
    });

    if ($('#id_school option:selected').text() !== "Other"){
        $('#id_school_other').parent().hide();
    }
    $('#id_school').on('change', function(){
         let selection = $('#id_school option:selected').text();
         if (selection === "Other"){
            $('#id_school_other').parent().show();
         }
         else{
             $('#id_school_other').parent().hide();
         }
    });

    const http = require('http'); // importing http

    /**
     * Function to keep heroku app awake. Currently this pings the
     * hacklahoma-stats.herokuapp.com domain every 20 minutes. Keep this until we
     * find a better hosting solution, but while we have the free plan of heroku we
     * need to keep this to keep it awake.
     */ 
    setInterval(() => {
        const options = {
            host: 'hacklahoma-register-2021.herokuapp.com',
            port: 80,
            path: '/',
        };
        http.get(options, (res) => {
            res.on('data', () => {
                try {
                    // optional logging... disable after it's working
                    console.log('Ping!');
                } catch (err) {
                    console.log(err.message);
                }
            });
        }).on('error', (err) => {
            console.log(`Error: ${err.message}`);
        });
      }, 20 * 60 * 1000); // load every 20 minutes
})
