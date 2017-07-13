import os

BOT_TOKEN = os.environ.get('TOKEN')

PORT = int(os.environ.get('PORT', '5000'))
BASE_WEBHOOK_URL = 'https://naccbot.herokuapp.com/'

NACC_TENDERS_URL = 'http://nacc.or.ke/tenders'

DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_URI = 'mongodb://austinewuncler:{' \
         '}@ds139438.mlab.com:39438/naccbot'.format(DB_PASSWORD)

NACC_BACKEND_SERVER = 'http://197.156.139.54:100/API/Users'

AUTH_HEADER = {
    'Authorization': 'Bearer Gx5GjvIMWv5dZsnm8jKphDqTK3PSx4BmUvl8rFSM6dkfPf3VrWiRhLUJwOBQIkkmh61Gk488jHfcOc2tlffS41_rKFsq-JoFOeFJ3G4k5eoG35V1SVMoppl9gx1Up3EreEt6vW1zgq3WwVtaRx0GKPa7vL2Qol3YIQzmcAZ7qyWulOoCATFh43S4aq-_XqCdVVmw87L_6_uzDv2uDtJ4MTa0Yh1UXFovKQWWDycDFAyQ_3xmYLz_k8qOAeY0wQABRe8VO3oiSPHMmn3YU_k9yzE2m7QSpZGve2-GaSow5afLZ9wU2POM79_b6erqJ7fnAIKbjQGAWXLLLaaucHhEBPWENrDhwZIREkALdKovzqMva0g506wMgH76Uc0fC2B1e1ZKooZHGvZCOhJUijfsO3ec1U-bKZ4Wx1ZN0uYcaVu9Gfxs6bXyRkPeswjySsTG3B4ABD5DxSLBhawoidWay2qfTOM9lU1GTWYN-OBslfiY7SgvGLsCiWKXSPlpug-c'
}
