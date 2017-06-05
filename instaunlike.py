import time
import datetime
import random


class InstaUnlike:
    def __init__(self, operation, repository, content_manager, configuration):
        self.operation = operation
        self.content_manager = content_manager
        self.repository = repository
        self.configuration = configuration

        self.max_unlikes_per_hour = self.configuration.instalike_max_likes_per_hour

        # Timing.
        self.next_unlike_time = 0
        self.like_time_delta = (60 * 60) // self.max_likes_per_hour

        self.working_day = datetime.date.today().day

        # Instance stats.
        self.unlikes = 0
        self.failed_unlikes = 0
        self.hourly_unlikes = 0

        self.t0 = time.time()
        self.t1 = 0

    def unlike(self, media):
        response = self.operation.unlike(media.id)

        if (not response):
            self.failed_to_unlike()
            return False

        if (response.status_code != 200):
            self.failed_to_unlike()
            return False

#        self.repository.persist_unlike(media)
#        self.photo_unliked()

        return True

    def act(self):
        if (not self.can_act()):
            return

        if (time.time() < self.next_like_time):
            return

        media = self.content_manager.get_next_media()
        if (media):
            self.unlike(media)
        else:
            self.log('Could not get media.')
        self.like_timeout()

    # Has to be reworked.
    def can_act(self):
        self.t1 = time.time()
        # hour elapsed
        if ((self.t1 - self.t0) >= 60 * 60):
            print('# of likes in last hour: {0}'.format(self.hourly_unlikes))
            self.t0 = time.time()
            self.hourly_unlikes = 0
            return True
        elif self.hourly_unlikes > self.max_unlikes_per_hour:
            return False
        return True

    def like_timeout(self):
        min_timeout = self.like_time_delta - (self.like_time_delta // 2)
        max_timeout = self.like_time_delta + (self.like_time_delta // 2)

        next_in = random.randint(min_timeout, max_timeout)
        self.next_unlike_time = time.time() + next_in
        self.get_stats()

    def photo_unliked(self):
        self.unlikes += 1
        self.unhourly_likes += 1

    def failed_to_unlike(self):
        self.failed_unlikes += 1
        self.hourly_unlikes += 1

    def get_stats(self):
        self.t1 = time.time()
        per_hour = ((self.unlikes + self.failed_unlikes) * 60 * 60) // (
        1 if (self.t1 - self.t0) == 0 else self.t1 - self.t0)
        self.log('#######################################')
        self.log('----------------UNLIKES------------------')
        self.log('total time: {0:.0f}s'.format(self.t1 - self.t0))
        self.log('unlikes: {0}'.format(self.unlikes))
        self.log('failed unlikes: {0}'.format(self.failed_unlikes))
        self.log('estimated unlikes per hour: {0:.0f}'.format(per_hour))
        self.log('next unlike in: {0:.0f}s'.format(self.next_like_time - time.time()))
        self.log('photos to unlike: {0}'.format(self.content_manager.get_media_count()))

    def log(self, text):
        print(text)
