import sys
import os.path
import random
from main import url_for

def save_termform_clip(form):
    '''
    Helper function that takes a TermForm with create_clip_with_file uploaded by the user, saves the file
    to disk, and returns the URL to that file (which should be used as the URL for a new Clip).
    '''
    destination_fname = (''.join([random.choice('abcdefghijklmnopqrstuvwzyz') for x in range(0, 16)])) + \
                        (os.path.splitext(form.create_clip_with_file.data.filename)[1])
    destination_path = os.path.join(sys.path[0], 'static', 'clips', destination_fname)
    destination_url  = url_for('static', filename=os.path.join('clips', destination_fname))
    form.create_clip_with_file.data.save(destination_path)
    return destination_url