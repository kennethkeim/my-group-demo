
// import events to new year form submission handler
$('#importev_form').on('submit', function(e){
     e.preventDefault();

     $.ajax({
         url: '/admin/importevents',
         type: "POST",
         data: $( this ).serialize(),
         success: function(data){
             $('#importev_form').trigger('reset');
             $('#col').append(`<div id="success_message">${data}</div>`);
         },
         error: function(jqXHR, textStatus, errorThrown){
            $('#col').append(`<div id="error_message">${errorThrown}: ${jqXHR.responseText}</div>`);
         }
     });
});
