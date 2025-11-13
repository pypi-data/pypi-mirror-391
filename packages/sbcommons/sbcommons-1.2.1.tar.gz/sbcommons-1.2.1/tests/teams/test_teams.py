from unittest.mock import patch
from sbcommons.teams import teams


class TestSendMessage:
    """Tests for the teams.send_message function"""
    
    def test_send_message_success(self):
        """Test successful message sending"""
        with patch('sbcommons.teams.teams.webhooks.post_to_webhook') as mock_post:
            mock_post.return_value = True
            
            result = teams.send_message(
                webhook_url="https://example.webhook.office.com/webhookb2/test",
                title="Test Title",
                msg="Test message"
            )
            
            assert result is True
            mock_post.assert_called_once()
            
            # Verify the call arguments
            call_args = mock_post.call_args
            assert call_args[1]['service'] == 'teams'
            assert call_args[1]['webhook_url'] == "https://example.webhook.office.com/webhookb2/test"
            
            # Verify the JSON structure
            json_data = call_args[1]['json']
            assert json_data['type'] == 'message'
            assert len(json_data['attachments']) == 1
            
    def test_send_message_failure(self):
        """Test failed message sending"""
        with patch('sbcommons.teams.teams.webhooks.post_to_webhook') as mock_post:
            mock_post.return_value = False
            
            result = teams.send_message(
                webhook_url="https://example.webhook.office.com/webhookb2/test",
                title="Test Title",
                msg="Test message"
            )
            
            assert result is False
            
    def test_adaptive_card_structure(self):
        """Test that the adaptive card has the correct structure"""
        with patch('sbcommons.teams.teams.webhooks.post_to_webhook') as mock_post:
            mock_post.return_value = True
            
            teams.send_message(
                webhook_url="https://example.webhook.office.com/webhookb2/test",
                title="My Title",
                msg="My Message"
            )
            
            json_data = mock_post.call_args[1]['json']
            attachment = json_data['attachments'][0]
            
            # Verify attachment structure
            assert attachment['contentType'] == 'application/vnd.microsoft.card.adaptive'
            assert 'content' in attachment
            
            # Verify adaptive card structure
            content = attachment['content']
            assert content['type'] == 'AdaptiveCard'
            assert content['$schema'] == 'http://adaptivecards.io/schemas/adaptive-card.json'
            assert content['version'] == '1.4'
            assert 'body' in content
            assert len(content['body']) == 2
            
    def test_title_text_block(self):
        """Test that the title TextBlock has correct properties"""
        with patch('sbcommons.teams.teams.webhooks.post_to_webhook') as mock_post:
            mock_post.return_value = True
            
            title_text = "Important Alert"
            teams.send_message(
                webhook_url="https://example.webhook.office.com/webhookb2/test",
                title=title_text,
                msg="Details here"
            )
            
            json_data = mock_post.call_args[1]['json']
            title_block = json_data['attachments'][0]['content']['body'][0]
            
            assert title_block['type'] == 'TextBlock'
            assert title_block['text'] == title_text
            assert title_block['weight'] == 'bolder'
            assert title_block['size'] == 'large'
            assert title_block['wrap'] is True
            
    def test_message_text_block(self):
        """Test that the message TextBlock has correct properties"""
        with patch('sbcommons.teams.teams.webhooks.post_to_webhook') as mock_post:
            mock_post.return_value = True
            
            message_text = "This is a detailed message with **markdown** support"
            teams.send_message(
                webhook_url="https://example.webhook.office.com/webhookb2/test",
                title="Alert",
                msg=message_text
            )
            
            json_data = mock_post.call_args[1]['json']
            message_block = json_data['attachments'][0]['content']['body'][1]
            
            assert message_block['type'] == 'TextBlock'
            assert message_block['text'] == message_text
            assert message_block['wrap'] is True
            
    def test_no_content_url_field(self):
        """Test that contentUrl field is not present in the attachment"""
        with patch('sbcommons.teams.teams.webhooks.post_to_webhook') as mock_post:
            mock_post.return_value = True
            
            teams.send_message(
                webhook_url="https://example.webhook.office.com/webhookb2/test",
                title="Test",
                msg="Test"
            )
            
            json_data = mock_post.call_args[1]['json']
            attachment = json_data['attachments'][0]
            
            # Verify contentUrl is not in the attachment
            assert 'contentUrl' not in attachment
            
    def test_special_characters_in_message(self):
        """Test handling of special characters in title and message"""
        with patch('sbcommons.teams.teams.webhooks.post_to_webhook') as mock_post:
            mock_post.return_value = True
            
            title = "Alert: System <Error>"
            message = "Error occurred at 10:30 AM\nDetails: \"Connection failed\""
            
            result = teams.send_message(
                webhook_url="https://example.webhook.office.com/webhookb2/test",
                title=title,
                msg=message
            )
            
            assert result is True
            json_data = mock_post.call_args[1]['json']
            body = json_data['attachments'][0]['content']['body']
            
            assert body[0]['text'] == title
            assert body[1]['text'] == message
