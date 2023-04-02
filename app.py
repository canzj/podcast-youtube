import logging
import os

from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for

import podcast

app = Flask("Youtube-to-Podcast")
# Set up the logging
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(exc_info)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

module_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(module_dir)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3'}


@app.route('/')
def index():
    channels = podcast.query_channels()
    return render_template('index.html', channels=channels)


@app.route('/api/channels', methods=['GET'])
def get_channels():
    channels = podcast.query_channels()
    return jsonify(channels)


@app.route('/api/channels', methods=['POST'])
def create_channel():
    rss_url = request.form['rss_url']
    try:
        channel_id = podcast.add_one_channel(rss_url)
        return redirect(url_for('get_feed', channel_id=channel_id), code=302)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/channels/<channel_id>', methods=['PUT'])
def update_channel(channel_id):
    rss_url = request.form['rss_url']
    description = request.form['description']
    title = request.form['title']
    podcast.update_one_channel(channel_id, rss_url, description, title)
    return jsonify({'success': True})


@app.route('/api/channels/<channel_id>', methods=['DELETE'])
def remove_channel(channel_id):
    podcast.delete_one_channel(channel_id)
    return jsonify({'success': True})


@app.route('/api/channels/<channel_id>/fetch', methods=['POST'])
def fetch_channel(channel_id):
    channel = podcast.fetch_one_channel(channel_id)
    podcast.fetch_one_channel(channel)
    return jsonify({'success': True})


@app.route('/feed/<channel_id>')
def get_feed(channel_id):
    feed_path = podcast.get_feed_path(channel_id)
    return send_from_directory(os.path.dirname(feed_path), os.path.basename(feed_path), mimetype='application/rss+xml')


@app.route('/audio/<channel_id>/<path:audio_name>')
def get_audio(channel_id, audio_name):
    # if allowed_file(audio_name):
    audio_directory = podcast.get_audio_directory(channel_id)
    return send_from_directory(audio_directory, audio_name, mimetype='audio/mpeg', conditional=True, as_attachment=False)


# The following functions are used by the template
@app.context_processor
def utility_processor():
    def channel_id(channel):
        return channel.get_channel_id()

    return dict(channel_id=channel_id)


if __name__ == '__main__':
    podcast.setup(1)
    app.run(debug=True, host="0.0.0.0", port=50002)
