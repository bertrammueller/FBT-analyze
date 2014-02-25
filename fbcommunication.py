import fbconsole as fb

class FBComm:
    def __init__(self, group_id, actor_id):
        self.group_id = group_id
        self.actor_id = actor_id
        fb.AUTH_SCOPE = ['read_stream', 'user_groups']
        fb.authenticate()
    
    def get_updatetime(self):
        update_info = fb.fql('SELECT update_time FROM group WHERE ' +
                             'gid=' + self.group_id)
        return long(update_info[0]['update_time'])

    def read_stream(self, min_time):
        return fb.fql('SELECT post_id, message FROM stream WHERE ' + 
                      'source_id=' + self.group_id + 
                      ' AND actor_id=' + self.actor_id +
                      ' AND created_time>{}'.format(min_time))

    def read_comments(self, post_id, min_time):
        return fb.fql('SELECT text FROM comment WHERE ' +
                      'post_id="' + post_id +
                      '" AND fromid=' + self.actor_id +
                      ' AND time>{}'.format(min_time))
