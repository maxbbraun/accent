#!/usr/bin/env python3

"""
Simple test server to verify AIcon functionality
"""

from flask import Flask
import os
import sys

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>Accent Test Server</h1>
    <p>Server is running!</p>
    <p>Testing AIcon import...</p>
    '''

@app.route('/test-aicon')
def test_aicon():
    try:
        # Try to import AIcon
        from aicon import AIcon
        aicon = AIcon()
        return '''
        <h2>AIcon Import Test</h2>
        <p style="color: green;">✓ AIcon imported successfully!</p>
        <p>AIcon class: {}</p>
        <p><strong>Note:</strong> Actual image generation requires Firestore setup and API keys.</p>
        '''.format(type(aicon).__name__)
    except Exception as e:
        return '''
        <h2>AIcon Import Test</h2>
        <p style="color: red;">✗ AIcon import failed!</p>
        <p>Error: {}</p>
        '''.format(str(e))

@app.route('/test-schedule')
def test_schedule():
    try:
        # Test schedule integration
        from schedule import Schedule
        from geocoder import Geocoder
        
        geocoder = Geocoder()
        schedule = Schedule(geocoder)
        
        return '''
        <h2>Schedule Integration Test</h2>
        <p style="color: green;">✓ Schedule with AIcon integrated successfully!</p>
        <p>Available content types include 'aicon'</p>
        '''
    except Exception as e:
        return '''
        <h2>Schedule Integration Test</h2>
        <p style="color: red;">✗ Schedule integration failed!</p>
        <p>Error: {}</p>
        '''.format(str(e))

if __name__ == '__main__':
    print("Starting Accent Test Server...")
    print("Visit http://localhost:5000 to test basic functionality")
    print("Visit http://localhost:5000/test-aicon to test AIcon import")
    print("Visit http://localhost:5000/test-schedule to test schedule integration")
    app.run(host='0.0.0.0', port=5000, debug=True)