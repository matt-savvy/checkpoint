$(document).ready(function () {
    console.log('sanity');
    //**********************************************
    //* Constats
    //**********************************************
    var ENTRY_STATUS_ENTERED    = 0;
    var ENTRY_STATUS_RACING     = 1;
    var ENTRY_STATUS_PROCESSING = 5;
    var ENTRY_STATUS_FINISHED   = 2;
    var ENTRY_STATUS_DQD        = 3;
    var ENTRY_STATUS_DNF        = 4;

    var csrftoken = getCookie('csrftoken');
    var selectedRacerNumber;

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        console.log(e.target.id);
        if (e.target.id == 'racerinfo-tab') {
          racerInfo();
        } else if (e.target.id == 'start-tab') {
          startRacer();
        } else if (e.target.id == 'finish-tab') {
          finishRacer();
        } else if (e.target.id == 'dq-tab') {
          dqRacer();
        } else if (e.target.id == 'dnf-tab') {
          dnfRacer();
        } else if (e.target.id == 'run-entry-tab') {
          runEntry();
        } else if (e.target.id == 'award-tab') {
          awardRacer();
        } else if (e.target.id == 'deduct-tab') {
          deductRacer();
        } else if (e.target.id == 'current-tab') {
          currentlyRacing();
        } else if (e.target.id == 'not-tab') {
          notRaced();
        } else if (e.target.id == 'standings-tab') {
          standings();
        } else if (e.target.id == 'status-tab') {
          status();
        } else if (e.target.id == 'mass-start-tab') {
          massStart();
        }
      });

    $('#standings-tab').click(function () {
      standings();
    });

    racerInfo();

    //**********************************************
    //* Racer Info
    //**********************************************

    function racerInfo() {
      $.ajax({
          url: '/racecontrol/ajax/racerinfo/' + raceId + '/  ',
          type: 'GET',
          beforeSend: function (request) {
              request.setRequestHeader('X-CSRFToken', csrftoken);
            },

          success: function (data, textStatus, xhr) {
              $('#racerinfo').html(data);
              setupRacerInfo();
            },

          error: function (xhr, textStatus, errorThrown) {

          },
        });
    }

    function setupRacerInfo() {
      $('#racer-info-racer-number-form').submit(function (e) {
              e.preventDefault();
              selectedRacerNumber = $('#racer-info-racer-number').val();

              $.ajax({
                  url: '/racecontrol/ajax/racerdetail?race=' + raceId + '&racer=' + selectedRacerNumber,
                  type: 'GET',
                  beforeSend: function (request) {
                      request.setRequestHeader('X-CSRFToken', csrftoken);
                    },

                  success: function (data, textStatus, xhr) {
                      $('#racer-info-detail-view').html(data);
                      $('#racer-info-racer-number').val('');
                      $('#racer-info-racer-number').focus();

                      $('#update-racer-notes').click(function () {
                          var request = Object();
                          request.racer = $(event.currentTarget).attr('racer-number');
                          request.race = raceId;
                          request.notes = $('#racer_notes').val();
                          var json = JSON.stringify(request);
                          $.ajax({
                              url: '/ajax/racernotes/',
                              type: 'POST',
                              contentType: 'application/json',
                              data: json,
                              beforeSend: function (request) {
                                  request.setRequestHeader('X-CSRFToken', csrftoken);
                                },

                              success: function (data, textStatus, xhr) {

                              },

                              error: function (xhr, textStatus, errorThrown) {
                              },
                            });
                        });

                    },

                  error: function (xhr, textStatus, errorThrown) {

                  },
                });
            });

    }


    //**********************************************
    //* Start Racer
    //**********************************************
    var startRacerInfoCheck = false;
    var startWristbandCheck = false;

    function startRacer() {
      $.ajax({
          url: '/racecontrol/ajax/start/' + raceId + '/  ',
          type: 'GET',
          beforeSend: function (request) {
              request.setRequestHeader('X-CSRFToken', csrftoken);
            },

          success: function (data, textStatus, xhr) {
              $('#start').html(data);
              setupStartRacer();
            },

          error: function (xhr, textStatus, errorThrown) {

          },
        });
    }

    function setupStartRacer() {
      startRacerInfoCheck = false;
      startWristbandCheck = false;

      $('#start-racer-progress').hide();
      $('#start-buttons').hide();
      $('#start-success').hide();
      $('#start-racer-button').prop('disabled', true);
      $('#start-racer-number').keyup(function () {
          if ($('#start-racer-number').val().length == 3) {
            selectedRacerNumber = $('#start-racer-number').val();
            $('#start-racer-number').prop('disabled', true);
            $('#start-racer-progress').show();
            lookupRacerForStart(true);
          }
        });

      $('#start-racer-info-check-button').click(function () {
          startRacerInfoCheck = !startRacerInfoCheck;
          checkStartButtonAvailability();
          if (startRacerInfoCheck) {
              $('#start-racer-info-check-button').removeClass('btn-default');
              $('#start-racer-info-check-button').addClass('btn-success');
          } else {
              $('#start-racer-info-check-button').addClass('btn-default');
              $('#start-racer-info-check-button').removeClass('btn-success');
          }
      });

      $('#start-wristband-check-button').click(function () {
          startWristbandCheck = !startWristbandCheck;
          checkStartButtonAvailability();
          if (startWristbandCheck) {
              $('#start-wristband-check-button').removeClass('btn-default');
              $('#start-wristband-check-button').addClass('btn-success');
          } else {
              $('#start-wristband-check-button').addClass('btn-default');
              $('#start-wristband-check-button').removeClass('btn-success');
          }
      });

      $('#start-racer-button').click(function () {
          $('#start-racer-number').prop('disabled', true);
          startRacerInRace();
      });
    }

    function lookupRacerForStart(showButtons) {
      lookupRacer(selectedRacerNumber,
      function (raceEntry) {
          $('#start-racer-progress').hide();
          $('#start-racer-number').prop('disabled', false);
          $('#start-racer-number').val('');
          $('#start-racer-info').html(racerTemplate(raceEntry));
          if (showButtons) {
              if (raceEntry.entry_status == 0) {
                  $('#start-buttons').show();
              }
          } else {
              $('#start-buttons').hide();
          }

      },

      function () {
          $('#start-racer-progress').hide();
          $('#start-racer-number').prop('disabled', false);
          $('#start-racer-info').html(racer404Template($('#start-racer-number').val()));
          $('#start-racer-number').val('');
          $('#start-racer-number').focus();
          $('#start-buttons').hide();
      }
  );
    }

    function checkStartButtonAvailability() {
      if (startRacerInfoCheck && startWristbandCheck) {
          $('#start-racer-button').removeClass('btn-danger');
          $('#start-racer-button').addClass('btn-success');
          $('#start-racer-button').prop('disabled', false);
      } else {
          $('#start-racer-button').addClass('btn-danger');
          $('#start-racer-button').removeClass('btn-success');
          $('#start-racer-button').prop('disabled', true);
      }
    }

    function startRacerInRace() {
        fullScreenLoadingScreen();
        var request = Object()
        request.racer = selectedRacerNumber;
        request.race = raceId;
        var json = JSON.stringify(request);
        $.ajax({
            url: '/ajax/startracer/',
            type: 'POST',
            contentType: 'application/json',
            data: json,
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                fullScreenLoadingScreen();
                lookupRacerForStart(false);
                $('#start-due-back-time').text(data.due_back);
                $('#start-success').show();
                $('#start-buttons').hide();
                $('#start-racer-number').focus();

            },
            error: function(xhr, textStatus, errorThrown) {
                fullScreenLoadingScreen();
            }
        });

    }

    //**********************************************
    //* Finish Racer
    //**********************************************
    var finishRacerInfoCheck = false

    function finishRacer() {
        $.ajax({
            url: '/racecontrol/ajax/finish/' + raceId + '/',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#finish').html(data);
                setupFinishRacer();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    function setupFinishRacer() {
        finishRacerInfoCheck = false
        finishRacerNumberOfPackages = false;
        $('#finish-racer-progress').hide();
        $('#finish-buttons').hide();
        $('#finish-success').hide();
        $('#finish-racer-button').prop('disabled', true);
        $('#number-of-tickets-form-group').removeClass("has-success");
        $('#number-of-tickets-form-group').addClass("has-warning");
        $('#finish-racer-info-check-button').addClass('btn-default');
        $('#finish-racer-info-check-button').removeClass('btn-success');
        $('#finish-racer-number').keyup(function() {
            if ($('#finish-racer-number').val().length == 3) {
                selectedRacerNumber = $('#finish-racer-number').val();
                $('#finish-racer-number').prop('disabled', true);
                $('#finish-racer-progress').show();
                lookupRacerForFinish(true);
        }
        });

        $('#finish-racer-info-check-button').click(function() {
            finishRacerInfoCheck = !finishRacerInfoCheck;
            checkFinishButtonAvailability();
            if (finishRacerInfoCheck) {
                $('#finish-racer-info-check-button').removeClass('btn-default');
                $('#finish-racer-info-check-button').addClass('btn-success');
            }
            else {
                $('#finish-racer-info-check-button').addClass('btn-default');
                $('#finish-racer-info-check-button').removeClass('btn-success');
            }
        });

        $('#finish-racer-button').click(function() {
            $('#finish-racer-button').prop('disabled', true);
            finishRacerInRace();
        });
    }

    function lookupRacerForFinish(showButtons) {
        lookupRacer(selectedRacerNumber,
        function(raceEntry) {
            $('#finish-racer-progress').hide();
            $('#finish-racer-number').prop('disabled',false);
            $('#finish-racer-number').val('');
            $('#finish-racer-info').html(racerTemplate(raceEntry));
            if (showButtons) {
                if (raceEntry.entry_status == ENTRY_STATUS_RACING || raceEntry.entry_status == ENTRY_STATUS_PROCESSING) {
                    $('#finish-buttons').show();
                }
            }
            else {
                $('#finish-buttons').hide();
            }

        },
        function() {
            $('#finish-racer-progress').hide();
            $('#finish-racer-number').prop('disabled', false);
            $('#finish-racer-info').html(racer404Template(selectedRacerNumber));
            $('#finish-racer-number').val('');
            $('#finish-racer-number').focus();
            $('#finish-buttons').hide();
        }
    );
    }

    function checkFinishButtonAvailability() {
        if (finishRacerInfoCheck) {
            $('#finish-racer-button').removeClass('btn-danger');
            $('#finish-racer-button').addClass('btn-success');
            $('#finish-racer-button').prop('disabled', false);
        }
        else {
            $('#finish-racer-button').addClass('btn-danger');
            $('#finish-racer-button').removeClass('btn-success');
            $('#finish-racer-button').prop('disabled', true);
        }
    }

    function finishRacerInRace() {
        fullScreenLoadingScreen();
        var request = Object()
        request.racer = selectedRacerNumber;
        request.race = raceId;
        request.number_of_tickets = parseInt($('#finish-number-of-tickets').val());
        var json = JSON.stringify(request);
        $.ajax({
            url: '/ajax/finishracer/',
            type: 'POST',
            contentType: 'application/json',
            data: json,
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                fullScreenLoadingScreen();
                lookupRacerForFinish(false);
                $('#finish-success').show();
                $('#finish-buttons').hide();
                $('#finish-racer-number').focus();
                $('#final-time').text(data.final_time);

            },
            error: function(xhr, textStatus, errorThrown) {
                fullScreenLoadingScreen();
            }
        });

    }

    //**********************************************
    //* DQ Racer
    //**********************************************
    function dqRacer() {
        $.ajax({
            url: '/racecontrol/ajax/dq/' + raceId + '/',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#dq').html(data);
                setupDqRacer();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    function setupDqRacer() {
        $('#dq-racer-progress').hide();
        $('#dq-buttons').hide();
        $('#un-dq-buttons').hide();
        $('#dq-racer-button').prop('disabled', true);
        $('#dq-racer-success').hide();
        $('#un-dq-racer-success').hide();

        $('#dq-racer-number').keyup(function() {
            $('#dq-racer-success').hide();
            $('#un-dq-racer-success').hide();
            if ($('#dq-racer-number').val().length == 3) {
                selectedRacerNumber = $('#dq-racer-number').val();
                $('#dq-racer-number').prop('disabled', true);
                $('#dq-racer-progress').show();
                lookupRacerForDQ(true);
        }
        });

        $("#dq-reason").keyup(function() {
            if ($('#dq-reason').val().length > 0) {
                $('#dq-racer-button').prop('disabled', false);
            }
            else {
                $('#dq-racer-button').prop('disabled', true);
            }
        });

        $('#dq-racer-button').click(function() {
            fullScreenLoadingScreen();
            var request = Object()
            request.racer = selectedRacerNumber;
            request.race = raceId;
            request.dq_reason = $('#dq-reason').val();
            var json = JSON.stringify(request);
            $.ajax({
                url: '/ajax/dqracer/',
                type: 'POST',
                contentType: 'application/json',
                data: json,
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(data, textStatus, xhr) {
                    fullScreenLoadingScreen();
                    lookupRacerForDQ(false);
                    $('#dq-racer-success').show();
                    $('#dq-reason').val("");
                    $('#dq-buttons').hide();
                    $('#dq-racer-number').focus();

                },
                error: function(xhr, textStatus, errorThrown) {
                    fullScreenLoadingScreen();
                }
            });
        });

        $('#un-dq-racer-button').click(function() {
            var check = window.confirm("Are you sure you want to un-dq this racer?");
            if (check) {
                fullScreenLoadingScreen();
                var request = Object()
                request.racer = selectedRacerNumber;
                request.race = raceId;
                var json = JSON.stringify(request);
                $.ajax({
                    url: '/ajax/undqracer/',
                    type: 'POST',
                    contentType: 'application/json',
                    data: json,
                    beforeSend: function (request) {
                        request.setRequestHeader("X-CSRFToken", csrftoken);
                    },
                    success: function(data, textStatus, xhr) {
                        fullScreenLoadingScreen();
                        lookupRacerForDQ(false);
                        $('#un-dq-racer-success').show();
                        $('#un-dq-buttons').hide();
                        $('#dq-racer-number').focus();

                    },
                    error: function(xhr, textStatus, errorThrown) {
                        fullScreenLoadingScreen();
                    }
                });
            }
        });

    }

    function lookupRacerForDQ(showButtons) {
        lookupRacer(selectedRacerNumber,
        function(raceEntry) {
            $('#dq-racer-progress').hide();
            $('#dq-racer-number').prop('disabled',false);
            $('#dq-racer-number').val('');
            $('#dq-racer-info').html(racerTemplate(raceEntry));
            if (showButtons) {
                if (raceEntry.entry_status == ENTRY_STATUS_DQD) {
                    $('#un-dq-buttons').show();
                }
                else {
                    $('#dq-buttons').show();
                }
            }
            else {
                $('#dq-buttons').hide();
                $('#un-dq-buttons').hide();
            }

        },
        function() {
            $('#dq-racer-progress').hide();
            $('#dq-racer-number').prop('disabled', false);
            $('#dq-racer-info').html(racer404Template(selectedRacerNumber));
            $('#dq-racer-number').val('');
            $('#dq-racer-number').focus();
            $('#dq-buttons').hide();
        }
    );
    }

    //**********************************************
    //* DNF Racer
    //**********************************************
    function dnfRacer() {
        $.ajax({
            url: '/racecontrol/ajax/dnf/' + raceId + '/',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#dnf').html(data);
                setupDNFRacer();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    function setupDNFRacer() {
        $('#dnf-buttons').hide();
        $('#dnf-racer-success').hide();
        $('#dnf-racer-progress').hide();
        $('#dnf-racer-number').keyup(function() {
            $('#dnf-racer-success').hide();
            if ($('#dnf-racer-number').val().length == 3) {
                selectedRacerNumber = $('#dnf-racer-number').val();
                $('#dnf-racer-number').prop('disabled', true);
                $('#dnf-racer-progress').show();
                lookupRacerForDNF(true);
        }
        });

        $('#dnf-racer-button').click(function() {
            fullScreenLoadingScreen();
            var request = Object()
            request.racer = selectedRacerNumber;
            request.race = raceId;
            var json = JSON.stringify(request);
            $.ajax({
                url: '/ajax/dnfracer/',
                type: 'POST',
                contentType: 'application/json',
                data: json,
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(data, textStatus, xhr) {
                    fullScreenLoadingScreen();
                    lookupRacerForDNF(false);
                    $('#dnf-racer-success').show();
                    $('#dnf-buttons').hide();
                    $('#dnf-racer-number').focus();

                },
                error: function(xhr, textStatus, errorThrown) {
                    fullScreenLoadingScreen();
                }
            });
        });

    }

    function lookupRacerForDNF(showButtons) {
        lookupRacer(selectedRacerNumber,
        function(raceEntry) {
            $('#dnf-racer-progress').hide();
            $('#dnf-racer-number').prop('disabled',false);
            $('#dnf-racer-number').val('');
            $('#dnf-racer-info').html(racerTemplate(raceEntry));
            if (showButtons) {
                if (raceEntry.entry_status == ENTRY_STATUS_RACING) {
                    $('#dnf-buttons').show();
                }
            }
            else {
                $('#dnf-buttons').hide();
            }

        },
        function() {
            $('#dnf-racer-progress').hide();
            $('#dnf-racer-number').prop('disabled', false);
            $('#dnf-racer-info').html(racer404Template(selectedRacerNumber));
            $('#dnf-racer-number').val('');
            $('#dnf-racer-number').focus();
            $('#dnf-buttons').hide();
        }
    );
    }

    //**********************************************
    //* Run Entry
    //**********************************************
    function runEntry() {
        $.ajax({
            url: '/racecontrol/ajax/runentry/' + raceId + '/',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#run-entry').html(data);
                setupRunEntry();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    function setupRunEntry() {
        $('#run-entry-racer-number').prop('disabled', false);
        $('#run-entry-progress').hide();
        $('#run-entry-racer-number').keyup(function() {
            if ($('#run-entry-racer-number').val().length == 3) {
                selectedRacerNumber = $('#run-entry-racer-number').val();
                $('#run-entry-racer-number').prop('disabled', true);
                $('#run-entry-progress').show();
                getRacerRuns(function() {
                    $('#run-entry-racer-number').prop('disabled', false);
                    $('#run-entry-progress').hide();
                    setupRacerRunEntry();
                });
            }
        });
    }

    function getRacerRuns(completion) {
        $.ajax({
            url: '/racecontrol/ajax/racerrunentry/' + raceId + '/' + selectedRacerNumber + '/',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#run-entry-racer-number').val("");
                $('#racer-run-entry').html(data);
                completion();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    function setupRacerRunEntry() {
        if (!$('#add-run-button').length) {
            $('#run-entry-racer-number').focus();
            return;
        }
        $('#add-run-field').focus();

        $('#add-run-button').click(function() {
            addRun($('#add-run-field').val());
        });

        $('#run-form').submit(function() {
            addRun($('#add-run-field').val());
            return false;
        });

        $('.delete-run-button').click(function() {
            deleteRun($(event.currentTarget).attr('run-id'));
        });
    }

    function addRun(jobId) {
        $('#run-error-text').text("");
        $('#run-entry-racer-number').prop('disabled', true);
        $('#add-run-field').prop('disabled', true);
        $('#add-run-button').button('loading');
        var request = Object()
        request.racer = parseInt(selectedRacerNumber);
        request.race = parseInt(raceId);
        request.job = parseInt(jobId);
        var json = JSON.stringify(request);
        $.ajax({
            url: '/ajax/run/',
            type: 'POST',
            contentType: 'application/json',
            data: json,
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#run-entry-racer-number').prop('disabled', false);
                getRacerRuns(function() {
                    setupRacerRunEntry();
                });

            },
            error: function(xhr, textStatus, errorThrown) {
                var error = JSON.parse(xhr.responseText);
                $('#run-error-text').text(error.detail);
                $('#add-run-button').button('reset');
                $('#add-run-field').val("");
                $('#add-run-field').prop('disabled', false);
                $('#run-entry-racer-number').prop('disabled', false);
                $('#add-run-field').focus();

            }
        });
    }

    function deleteRun(runId) {
        var request = Object()
        request.run = runId;
        var json = JSON.stringify(request);
        $.ajax({
            url: '/ajax/deleterun/',
            type: 'POST',
            contentType: 'application/json',
            data: json,
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#run-entry-racer-number').prop('disabled', false);
                getRacerRuns(function() {
                    setupRacerRunEntry();
                });

            },
            error: function(xhr, textStatus, errorThrown) {
                getRacerRuns(function() {
                    setupRacerRunEntry();
                });
            }
        });
    }

    //**********************************************
    //* Award Racer
    //**********************************************

    function awardRacer() {
        $.ajax({
            url: '/racecontrol/ajax/award/' + raceId + '/',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#award').html(data);
                setupAwardRacer();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    function setupAwardRacer() {
        $('#award-buttons').hide();
        $('#award-racer-success').hide();
        $('#award-racer-progress').hide();
        $('#award-racer-number').keyup(function() {
            $('#award-racer-success').hide();
            if ($('#award-racer-number').val().length == 3) {
                selectedRacerNumber = $('#award-racer-number').val();
                $('#award-racer-number').prop('disabled', true);
                $('#award-racer-progress').show();
                lookupRacerForAward(true);
        }
        });

        $('#award-racer-button').click(function() {
            fullScreenLoadingScreen();
            var request = Object()
            request.racer = selectedRacerNumber;
            request.race = raceId;
            request.award = $('#award-racer-amount').val();
            var json = JSON.stringify(request);
            $.ajax({
                url: '/ajax/awardracer/',
                type: 'POST',
                contentType: 'application/json',
                data: json,
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(data, textStatus, xhr) {
                    fullScreenLoadingScreen();
                    lookupRacerForAward(false);
                    $('#award-racer-success').show();
                    $('#award-buttons').hide();
                    $('#award-racer-number').focus();

                },
                error: function(xhr, textStatus, errorThrown) {
                    fullScreenLoadingScreen();
                }
            });
        });

    }

    function lookupRacerForAward(showButtons) {
        lookupRacer(selectedRacerNumber,
        function(raceEntry) {
            $('#award-racer-progress').hide();
            $('#award-racer-number').prop('disabled',false);
            $('#award-racer-number').val('');
            $('#award-racer-info').html(racerTemplate(raceEntry));
            if (showButtons) {
                $('#award-buttons').show();
                $('#award-racer-amount').val(raceEntry.supplementary_points);
                $('#award-racer-amount').focus();
            }
            else {
                $('#award-buttons').hide();
            }

        },
        function() {
            $('#award-racer-progress').hide();
            $('#award-racer-number').prop('disabled', false);
            $('#award-racer-info').html(racer404Template(selectedRacerNumber));
            $('#award-racer-number').val('');
            $('#award-racer-number').focus();
            $('#award-buttons').hide();
        }
    );
    }

    //**********************************************
    //* Deduct Racer
    //**********************************************

    function deductRacer() {
        $.ajax({
            url: '/racecontrol/ajax/deduct/' + raceId + '/',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#deduct').html(data);
                setupDeductRacer();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    function setupDeductRacer() {
        $('#deduct-buttons').hide();
        $('#deduct-racer-success').hide();
        $('#deduct-racer-progress').hide();
        $('#deduct-racer-number').keyup(function() {
            $('#deduct-racer-success').hide();
            if ($('#deduct-racer-number').val().length == 3) {
                selectedRacerNumber = $('#deduct-racer-number').val();
                $('#deduct-racer-number').prop('disabled', true);
                $('#deduct-racer-progress').show();
                lookupRacerForDeduct(true);
        }
        });

        $('#deduct-racer-button').click(function() {
            fullScreenLoadingScreen();
            var request = Object()
            request.racer = selectedRacerNumber;
            request.race = raceId;
            request.deduction = $('#deduct-racer-amount').val();
            var json = JSON.stringify(request);
            $.ajax({
                url: '/ajax/deductracer/',
                type: 'POST',
                contentType: 'application/json',
                data: json,
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(data, textStatus, xhr) {
                    fullScreenLoadingScreen();
                    lookupRacerForDeduct(false);
                    $('#deduct-racer-success').show();
                    $('#deduct-buttons').hide();
                    $('#deduct-racer-number').focus();

                },
                error: function(xhr, textStatus, errorThrown) {
                    fullScreenLoadingScreen();
                }
            });
        });

    }

    function lookupRacerForDeduct(showButtons) {
        lookupRacer(selectedRacerNumber,
        function(raceEntry) {
            $('#deduct-racer-progress').hide();
            $('#deduct-racer-number').prop('disabled',false);
            $('#deduct-racer-number').val('');
            $('#deduct-racer-info').html(racerTemplate(raceEntry));
            if (showButtons) {
                $('#deduct-buttons').show();
                $('#deduct-racer-amount').val(raceEntry.deductions);
                $('#deduct-racer-amount').focus();
            }
            else {
                $('#deduct-buttons').hide();
            }

        },
        function() {
            $('#deduct-racer-progress').hide();
            $('#deduct-racer-number').prop('disabled', false);
            $('#deduct-racer-info').html(racer404Template(selectedRacerNumber));
            $('#deduct-racer-number').val('');
            $('#deduct-racer-number').focus();
            $('#deduct-buttons').hide();
        }
    );
    }


    //**********************************************
    //* Currently Racing
    //**********************************************
    function currentlyRacing() {
        $.ajax({
            url: '/racecontrol/ajax/racing/' + raceId + '/',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#current').html(data);
                setupCurrentlyRacing();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    function setupCurrentlyRacing() {
        $('.dnf-current-racing').click(function() {
            $(event.currentTarget).button('loading');
            var racerNumber = $(event.currentTarget).attr('racer-number');
            var result = window.confirm("Are you sure you want to mark racer #" + racerNumber + " as DNF?");
            if (result) {
                fullScreenLoadingScreen();
                var request = Object()
                request.racer = racerNumber;
                request.race = raceId;
                var json = JSON.stringify(request);
                $.ajax({
                    url: '/ajax/dnfracer/',
                    type: 'POST',
                    contentType: 'application/json',
                    data: json,
                    beforeSend: function (request) {
                        request.setRequestHeader("X-CSRFToken", csrftoken);
                    },
                    success: function(data, textStatus, xhr) {
                        fullScreenLoadingScreen();
                        currentlyRacing();

                    },
                    error: function(xhr, textStatus, errorThrown) {
                        fullScreenLoadingScreen();
                        currentlyRacing();
                    }
                });
            }
            else {
                $(event.currentTarget).button('reset');
            }
        });
    }

    //**********************************************
    //* Not Raced
    //**********************************************
    function notRaced() {
        $.ajax({
            url: '/racecontrol/ajax/notraced/' + raceId + '/  ',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#not').html(data);
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    //**********************************************
    //*  Standings View
    //**********************************************
    function standings() {
        $.ajax({
            url: '/racecontrol/ajax/standings/' + raceId + '/  ',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#standings').html(data);
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    //**********************************************
    //* Race Status
    //**********************************************

    function status() {
        $.ajax({
            url: '/racecontrol/ajax/racestatus/' + raceId + '/',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#status').html(data);
                setupStatus();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    function setupStatus() {
        $('#set-race-start-time-button').click(function() {
            var request = Object()
            request.race = raceId;
            request.start_time = $('#race-start-datetime-date').val() + ' ' + $('#race-start-datetime-time').val();
            var json = JSON.stringify(request);
            $.ajax({
                url: '/ajax/setracestarttime/',
                type: 'POST',
                contentType: 'application/json',
                data: json,
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(data, textStatus, xhr) {
                    status();
                },
                error: function(xhr, textStatus, errorThrown) {
                    alert("An error occured setting the start time");
                }
            });
        });

        $('#change-current-race-button').click(function() {
            var request = Object()
            request.race = raceId;
            var json = JSON.stringify(request);
            $.ajax({
                url: '/ajax/setcurrentrace/',
                type: 'POST',
                contentType: 'application/json',
                data: json,
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(data, textStatus, xhr) {
                    status();
                },
                error: function(xhr, textStatus, errorThrown) {
                    alert("An error occured setting the start time");
                }
            });
        });
    }

    //**********************************************
    //* Mass Start
    //**********************************************

    function massStart() {
        $.ajax({
            url: '/racecontrol/ajax/massstart/' + raceId + '/',
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                $('#mass-start').html(data);
                setupMassStart();
            },
            error: function(xhr, textStatus, errorThrown) {

            }
        });
    }

    function setupMassStart() {
        $('#mass-start-button').click(function() {
            var request = Object()
            request.race = raceId;
            var json = JSON.stringify(request);
            $.ajax({
                url: '/ajax/massstartcompanies/',
                type: 'POST',
                contentType: 'application/json',
                data: json,
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrftoken);
                },
                success: function(data, textStatus, xhr) {
                    massStart();
                },
                error: function(xhr, textStatus, errorThrown) {
                    alert("An error occured setting the start time");
                }
            });
        });
    }

    //**********************************************
    //*  Racer Lookup
    //**********************************************

    function lookupRacer(racerNumber, foundRacer, didNotFindRacer) {
        $.ajax({
            url: '/ajax/raceentry?racer=' + racerNumber + '&race=' + raceId,
            type: 'GET',
            beforeSend: function (request) {
                request.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(data, textStatus, xhr) {
                foundRacer(data);
            },
            error: function(xhr, textStatus, errorThrown) {
                didNotFindRacer();
            }
        });
    }

    function racerTemplate(raceEntry) {
        var tmplMarkup = $('#racer-info-template').html();
        var compiledTmpl = _.template(tmplMarkup, { raceEntry : raceEntry});
        return compiledTmpl;
    }

    function racer404Template(input) {
        var tmplMarkup = $('#racer-404-template').html();
        var compiledTmpl = _.template(tmplMarkup, { input : input});
        return compiledTmpl;
    }

    function miniRacerTemplate(raceEntry) {
        console.log(raceEntry);
        var tmplMarkup = $('#mini-racer-info-template').html();
        var compiledTmpl = _.template(tmplMarkup, { raceEntry : raceEntry});
        return compiledTmpl;
    }

    function miniRacer404Template(input) {
        var tmplMarkup = $('#mini-racer-404-template').html();
        var compiledTmpl = _.template(tmplMarkup, { input : input});
        return compiledTmpl;
    }

    //**********************************************
    //*  Full Screen loading
    //**********************************************
    //You should show this whenever you wish to block a user from doing any interaction.
    //This should be used ONLY forrace crucial server requests.

    var showingFullScreenLoad = false;

    function fullScreenLoadingScreen() {
        if (showingFullScreenLoad) {
            console.log("hide");
            $('#fullscreen-load').modal('hide');
            showingFullScreenLoad = false;
        }
        else {
            console.log("show");
            $('#fullscreen-load').modal();
            showingFullScreenLoad = true;
        }
    }

    //**********************************************
    //* CSRF Protection
    //**********************************************
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});
