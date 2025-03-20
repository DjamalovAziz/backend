<!-- README.md -->

## v0.0.1
<pre>
PRIORITY:
FIXME что-бы .bat не удалял /media/avatars/default/PROFILE.jpg

Plan:
Project
    90%:
    user:
        DONE change my password:
        get:
			DONE me
			DONE users
			DONE user
        DONE patch me
        DONE signup
        DONE signin
        DONE refresh token
        DONE delete me
        avatar:
            Single Avatar:
                TEST DELETE /users/my/avatar
            Multiple Avatar:
                UNSAFE:
                    TEST POST /users/me/avatars
                    TEST PATCH /users/me/avatars/{avatar_id}
                    TEST DELETE /users/me/avatars/{avatar_id}
                    TEST GET /users/me/avatars
                SAFE:
                    TEST GET /users/{user_id}/avatars
        reset password:
            email
            telegram
            sms
    DONE logging
    permissions:
        user
        organization
        branch
        relation

    60%:
        organization:
            get:
				DONE organizations
				DONE organization
            DONE patch organization
            delete organization
            DONE post organization
        branch:
            get:
				DONE branch
				DONE branchs
            DONE patch branch
            delete branch - Cascade
            DONE post branch
        relation:
            get:
				DONE relations
				DONE relation
            patch:
				DONE change role
            delete relation
            api documentation:
				DONE drf-yasg
				DONE drf-spectacular
            docker:
                basic надо исправить, проанализировать
        chat:
            get:
                groups
                group
                messages
            post:
                group
                add_participant
                add_message
            Websocket:
                TEST personal
                DONE group

    30%:
        push notifications:
			ios
			android
			browser
        internationalization & localization
        jet
        integrations:
			click
			payme
        caching:
			redis
        cybersecurity:
			basic еще раз протестировать, проанализировать
        deploy to server
        ci/cd:
		github actions
		auto testing
        микросервисы с grpc
        graphql
</pre>