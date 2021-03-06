

 // toggle active states on directory and event buttons
 var dirbtn = document.getElementById('dirbtn');
 var evbtn = document.getElementById('evbtn');
 evbtn.classList.add("active");
 dirbtn.classList.remove("active");

 // activate the jQuery UI datepicker
 $('#datepicker1').datepicker();
 $('#datepicker2').datepicker();


 // global variable to remember the id of last clicked event
 // the variable saves the event's database id, and is passed in along with form data anytime an existing event is modified
 selected_ev_id = 0;


 // initiate popups on all events a tags
 var popup_content = '<button class="btn btn-sm" id="edit_pop_btn"><i class="fas fa-pencil-alt"></i> edit</button>' + '<button class="btn btn-sm" id="del_pop_btn" data-toggle="modal" data-target="#del_modal" data-backdrop="static"><i class="fas fa-trash-alt"></i> delete</button>'

 $(".allev_btn").popover({
     animation: true,
     content: popup_content,
     placement: 'bottom',
     container: 'body',
     trigger: 'focus',
     html: true
 });

 // get the current date and scroll to the current month
 var months = ["","January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
 var date = new Date();
 var month_name = months[date.getMonth() +1];
 window.location.href = "#" + month_name;

 // in case I need to scroll a given number of pixels
 // var pixels = $(window).scrollTop() - 60;
 // $(window).scrollTop(pixels);








 // Event handlers.............................................................................................................

 // dismiss the navbar when a month is clicked in mobile
 $('.mobile_nav_btn').click(function() {
    $('.navbar-toggler').trigger('click');
 });


 // all events a tag click handler
 $('a.allev_btn').on('click', function(e){
     e.preventDefault();
     selected_ev_id = $(this).attr('id');
 });


 // show the 'add event' form
 $('#addev_btn').on('click', function(){

    // reset all the values in the form
     $('#addev_form').trigger('reset');

     // show the modal
     $('#addev_modal').modal({backdrop: 'static'},'show');
 });



 // prefill the 'edit event' form with all event info for clicked event
 // show the edit event form
 $('a.allev_btn').on('click', function(){
     var thistag = $(this);
     $('#edit_pop_btn').on('click', function(){
         // get all the data for the selected event from the html elements
         var title = thistag.children('h6').text();
         var type = thistag.attr('name');
         var date = thistag.siblings().attr('datetime');
         var formattedDate = `${date.substring(5, 7)}/${date.substring(8)}/${date.substring(0,4)}`;
         var time = thistag.children('time').attr('datetime');
         var location = thistag.children('div').text();
         var notes = thistag.children('p').text();

         // initialize the 'edit event' form with the data
         var modal = $('#editev_modal');
         modal.find('#title2').val(title);
         modal.find('#type2').val(type);
         modal.find('#datepicker2').val(formattedDate);
         modal.find('#time2').val(time);
         modal.find('#location2').val(location);
         modal.find('#notes2').val(notes);

         // show the modal
         modal.modal({backdrop: 'static'},'show');
     });
 });




 // add event form submission handler
 $('#addev_form').on('submit', function(e){
      e.preventDefault();
      $('#addev_modal').modal('hide');

      $.ajax({
          url: '/events',
          type: "POST",
          data: $( this ).serialize(),
          success: function(){
              location.reload();
          },
          error: function(jqXHR, textStatus, errorThrown){
              $('#response').html("<p><div style='color: red;'>" + textStatus + " " + errorThrown + ": </div>" + jqXHR.responseText + "</p>");
              $('#response_modal').modal('show');
          }
      });
 });


 // edit event form submission handler
 $('#editev_form').on('submit', function(e){
      e.preventDefault();
      $('#editev_modal').modal('hide');

      $.ajax({
          url: `/events/${selected_ev_id}`,
          type: "PUT",
          data: $( this ).serialize(),
          success: function(){
              location.reload();
          },
          error: function(jqXHR, textStatus, errorThrown){
              $('#response').html("<p><div style='color: red;'>" + textStatus + " " + errorThrown + ": </div>" + jqXHR.responseText + "</p>");
              $('#response_modal').modal('show');
          }
      });
 });



 // delete event form submission handler
 $('#delev_confirm').on('click', function(){
      $.ajax({
          url: `/events/${selected_ev_id}`,
          type: "DELETE",
          success: function(){
              location.reload();
          },
          error: function(jqXHR, textStatus, errorThrown){
              $('#response').html("<p><div style='color: red;'>" + textStatus + " " + errorThrown + ": </div>" + jqXHR.responseText + "</p>");
              $('#response_modal').modal('show');
          }
      });
 });
