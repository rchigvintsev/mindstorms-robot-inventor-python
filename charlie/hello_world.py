from mindstorms import MSHub

ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

hub = MSHub()

hub.status_light.on('cyan')
hub.light_matrix.set_orientation('right')
hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'direct', False)
hub.speaker.play_sound('Hello')
