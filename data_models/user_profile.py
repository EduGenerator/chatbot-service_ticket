# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.schema import Attachment


class UserProfile:
    """
      This is our application state. Just a regular serializable Python class.
    """

    def __init__(self, kind: str = None, genre: str = None, duration: str = None, contact: str = None, spread: str = None, ticket: int = None, time: str = None):
        self.kind = kind
        self.genre = genre
        self.duration = duration
        self.spread = spread
        self.contact = contact
        self.ticket = ticket
        self.time = time