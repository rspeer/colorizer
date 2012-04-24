class DemoSequence
  constructor: (events) ->
    @eventList = events
    @listPos = 0
    @running = false
    @audio = $('#theaudio')[0]

  play: =>
    @listPos = 0
    @running = true
    @audio.play()
    this.step()

  stop: =>
    @audio.pause()

  step: =>
    if @running
      window.setTimeout(this.step, 50)
      diff = @audio.currentTime
      event = @eventList[@listPos]
      if diff > event.time
        window.colors.handleResponse(event)
        @listPos += 1

$ ->
  seq = new DemoSequence(events)
  if not seq.running
    seq.play()
  window.seq = seq 
